# api/memory_manager.py

import sqlite3
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import logging
import os
from datetime import datetime

class MemoryManager:
    """
    Manages conversation history using a SQLite database and a FAISS index for semantic search.
    """
    def __init__(self, db_path='samantha.db', model_name='all-MiniLM-L6-v2'):
        self.db_path = db_path
        self.index_path = db_path.replace('.db', '.index')
        self.conn = None
        
        try:
            # Load the sentence transformer model for creating embeddings
            logging.info(f"Loading sentence transformer model: {model_name}...")
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logging.info("Model loaded successfully.")
            
            # Initialize database and FAISS index
            self._init_db()
            self._load_or_create_index()

        except Exception as e:
            logging.error(f"Error during MemoryManager initialization: {e}")
            raise

    def _init_db(self):
        """Initializes the SQLite database and creates the conversation table if it doesn't exist."""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = self.conn.cursor()
            # The 'id' is now the primary key for FAISS lookup
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    text TEXT NOT NULL
                )
            ''')
            self.conn.commit()
            logging.info("Database initialized successfully.")
        except sqlite3.Error as e:
            logging.error(f"Database error in _init_db: {e}")
            raise

    def _load_or_create_index(self):
        """Loads the FAISS index from disk or creates a new one if it doesn't exist."""
        if os.path.exists(self.index_path):
            try:
                logging.info(f"Loading existing FAISS index from {self.index_path}")
                self.index = faiss.read_index(self.index_path)
                logging.info(f"FAISS index loaded. Contains {self.index.ntotal} vectors.")
            except Exception as e:
                logging.error(f"Failed to load FAISS index: {e}. Rebuilding...")
                self.build_index_from_db()
        else:
            logging.info("No FAISS index found. Creating a new one.")
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.index = faiss.IndexIDMap(self.index) # Map vectors to DB IDs
            self.build_index_from_db()

    def build_index_from_db(self):
        """Rebuilds the entire FAISS index from the conversation history in the database."""
        logging.info("Building FAISS index from database...")
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, text FROM conversation")
        rows = cursor.fetchall()
        
        if not rows:
            logging.info("No conversations in DB to index.")
            return

        ids = np.array([row[0] for row in rows])
        texts = [row[1] for row in rows]
        
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
            # Ensure embeddings are float32 as required by FAISS
            embeddings = np.array(embeddings, dtype='float32')
            
            # Re-initialize the index and add vectors
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.index = faiss.IndexIDMap(self.index)
            self.index.add_with_ids(embeddings, ids)
            
            faiss.write_index(self.index, self.index_path)
            logging.info(f"Successfully built and saved index with {self.index.ntotal} entries.")
        except Exception as e:
            logging.error(f"Error during index build: {e}")
            raise

    def save_message(self, sender: str, text: str):
        """Saves a message to the database and updates the FAISS index."""
        try:
            cursor = self.conn.cursor()
            timestamp = datetime.utcnow().isoformat()
            cursor.execute("INSERT INTO conversation (timestamp, sender, text) VALUES (?, ?, ?)",
                           (timestamp, sender, text))
            self.conn.commit()
            message_id = cursor.lastrowid
            
            # Add the new message to the FAISS index
            embedding = self.model.encode([text], convert_to_tensor=False)
            embedding_np = np.array(embedding, dtype='float32')
            id_np = np.array([message_id], dtype='int64')
            
            self.index.add_with_ids(embedding_np, id_np)
            faiss.write_index(self.index, self.index_path) # Save index after each addition
            logging.info(f"Saved message from '{sender}' with ID {message_id} and updated index.")
            
        except Exception as e:
            logging.error(f"Failed to save message: {e}")

    def search_memory(self, query: str, top_k: int = 3) -> str:
        """
        Searches for the most relevant conversation snippets from memory based on semantic similarity.
        """
        if self.index.ntotal == 0:
            return "No memories found."

        try:
            logging.info(f"Searching memory for query: '{query}'")
            query_embedding = self.model.encode([query], convert_to_tensor=False)
            query_embedding_np = np.array(query_embedding, dtype='float32')

            # Search the index
            distances, ids = self.index.search(query_embedding_np, k=top_k)
            
            if ids.size == 0 or ids[0][0] == -1: # FAISS returns -1 for no result
                return "No relevant memories found."

            # Fetch the corresponding text from the DB
            relevant_ids = tuple(ids[0])
            if not relevant_ids:
                return "No relevant memories found."
            
            # The '?' placeholder syntax prevents SQL injection
            placeholders = ', '.join('?' for _ in relevant_ids)
            query_str = f"SELECT sender, text FROM conversation WHERE id IN ({placeholders}) ORDER BY timestamp DESC"
            
            cursor = self.conn.cursor()
            cursor.execute(query_str, relevant_ids)
            results = cursor.fetchall()
            
            # Format results for the prompt
            formatted_context = "\n".join([f"- {row[0]} said: '{row[1]}'" for row in results])
            return formatted_context
            
        except Exception as e:
            logging.error(f"Error during memory search: {e}")
            return "Could not retrieve memories due to an error."
            
    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")