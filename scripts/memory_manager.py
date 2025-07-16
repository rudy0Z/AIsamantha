import chromadb
from chromadb.config import Settings
import json
import sqlite3
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path
import os

class MemoryManager:
    def __init__(self, db_path="samantha_memory"):
        # Initialize ChromaDB for vector storage
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        
        # Create or get collection for memories
        self.memory_collection = self.chroma_client.get_or_create_collection(
            name="conversation_memories",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize sentence transformer for embeddings
        print("Loading sentence transformer...")
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # SQLite for structured data
        self.db_path = f"{db_path}/memories.db"
        self._init_sqlite_db()
        
        # Memory categories
        self.memory_categories = {
            'personal': ['family', 'friends', 'relationships', 'personal'],
            'work': ['job', 'work', 'career', 'office', 'colleague'],
            'health': ['health', 'doctor', 'medicine', 'exercise', 'sleep'],
            'emotions': ['feeling', 'emotion', 'mood', 'happy', 'sad', 'angry'],
            'goals': ['goal', 'dream', 'aspiration', 'want', 'hope', 'plan'],
            'experiences': ['experience', 'memory', 'remember', 'happened', 'event']
        }

    def _init_sqlite_db(self):
        """Initialize SQLite database for structured memory storage"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create memories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_input TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                emotion_data TEXT,
                category TEXT,
                importance_score REAL DEFAULT 5.0,
                context_data TEXT,
                embedding_id TEXT
            )
        ''')
        
        # Create emotion trends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emotion_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                avg_sentiment TEXT,
                avg_intensity REAL,
                dominant_emotions TEXT,
                total_interactions INTEGER
            )
        ''')
        
        # Create user profile table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_memory(self, conversation_entry):
        """Save conversation memory with vector embeddings"""
        try:
            # Generate embedding for the conversation
            combined_text = f"{conversation_entry['user_input']} {conversation_entry['ai_response']}"
            embedding = self.sentence_model.encode(combined_text).tolist()
            
            # Generate unique ID for this memory
            memory_id = f"memory_{datetime.now().timestamp()}"
            
            # Categorize the memory
            category = self._categorize_memory(conversation_entry['user_input'])
            
            # Calculate importance score
            importance = self._calculate_importance(conversation_entry)
            
            # Save to ChromaDB
            self.memory_collection.add(
                embeddings=[embedding],
                documents=[combined_text],
                metadatas=[{
                    'timestamp': conversation_entry['timestamp'],
                    'user_input': conversation_entry['user_input'],
                    'ai_response': conversation_entry['ai_response'],
                    'category': category,
                    'importance': importance
                }],
                ids=[memory_id]
            )
            
            # Save to SQLite
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO memories 
                (timestamp, user_input, ai_response, emotion_data, category, 
                 importance_score, embedding_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                conversation_entry['timestamp'],
                conversation_entry['user_input'],
                conversation_entry['ai_response'],
                json.dumps(conversation_entry.get('emotion', {})),
                category,
                importance,
                memory_id
            ))
            
            conn.commit()
            conn.close()
            
            # Update emotion trends
            self._update_emotion_trends(conversation_entry)
            
            print(f"Memory saved: {memory_id}")
            
        except Exception as e:
            print(f"Error saving memory: {e}")

    def get_relevant_context(self, query, limit=5):
        """Retrieve relevant memories for context"""
        try:
            # Generate embedding for the query
            query_embedding = self.sentence_model.encode(query).tolist()
            
            # Search similar memories
            results = self.memory_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            
            relevant_memories = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    relevant_memories.append({
                        'content': doc,
                        'timestamp': metadata['timestamp'],
                        'user_input': metadata['user_input'],
                        'ai_response': metadata['ai_response'],
                        'category': metadata['category'],
                        'importance': metadata['importance']
                    })
            
            return relevant_memories
            
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []

    def get_recent_memories(self, limit=10):
        """Get recent memories from SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, user_input, ai_response, emotion_data, category, importance_score
                FROM memories 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            memories = []
            for row in rows:
                memories.append({
                    'timestamp': row[0],
                    'user_input': row[1],
                    'ai_response': row[2],
                    'emotion': json.loads(row[3]) if row[3] else {},
                    'category': row[4],
                    'importance': row[5]
                })
            
            return memories
            
        except Exception as e:
            print(f"Error getting recent memories: {e}")
            return []

    def _categorize_memory(self, text):
        """Categorize memory based on content"""
        text_lower = text.lower()
        
        for category, keywords in self.memory_categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return 'general'

    def _calculate_importance(self, conversation_entry):
        """Calculate importance score for a memory"""
        base_score = 5.0
        
        # Emotion intensity affects importance
        emotion = conversation_entry.get('emotion', {})
        intensity = emotion.get('intensity', 5)
        
        # High intensity emotions are more important
        if intensity >= 8:
            base_score += 2
        elif intensity >= 6:
            base_score += 1
        elif intensity <= 3:
            base_score -= 1
        
        # Certain emotions are more memorable
        emotions = emotion.get('emotions', [])
        important_emotions = ['love', 'fear', 'anger', 'joy', 'sadness']
        if any(emo in important_emotions for emo in emotions):
            base_score += 1
        
        # Length of conversation affects importance
        text_length = len(conversation_entry['user_input']) + len(conversation_entry['ai_response'])
        if text_length > 200:
            base_score += 0.5
        
        # Personal topics are more important
        personal_keywords = ['family', 'love', 'death', 'birth', 'marriage', 'divorce', 'job', 'health']
        if any(keyword in conversation_entry['user_input'].lower() for keyword in personal_keywords):
            base_score += 1.5
        
        return min(max(base_score, 1.0), 10.0)

    def _update_emotion_trends(self, conversation_entry):
        """Update daily emotion trends"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            emotion = conversation_entry.get('emotion', {})
            
            if not emotion:
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if today's trend exists
            cursor.execute('SELECT * FROM emotion_trends WHERE date = ?', (today,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing trend
                current_interactions = existing[5]
                current_avg_intensity = existing[3]
                new_intensity = emotion.get('intensity', 5)
                
                # Calculate new average
                new_avg_intensity = ((current_avg_intensity * current_interactions) + new_intensity) / (current_interactions + 1)
                
                cursor.execute('''
                    UPDATE emotion_trends 
                    SET avg_intensity = ?, total_interactions = ?
                    WHERE date = ?
                ''', (new_avg_intensity, current_interactions + 1, today))
            else:
                # Create new trend entry
                cursor.execute('''
                    INSERT INTO emotion_trends 
                    (date, avg_sentiment, avg_intensity, dominant_emotions, total_interactions)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    today,
                    emotion.get('sentiment', 'neutral'),
                    emotion.get('intensity', 5),
                    json.dumps(emotion.get('emotions', [])),
                    1
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error updating emotion trends: {e}")

    def get_emotion_trends(self, days=7):
        """Get emotion trends for the past N days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT date, avg_sentiment, avg_intensity, dominant_emotions, total_interactions
                FROM emotion_trends 
                WHERE date >= ?
                ORDER BY date DESC
            ''', (start_date,))
            
            rows = cursor.fetchall()
            conn.close()
            
            trends = []
            for row in rows:
                trends.append({
                    'date': row[0],
                    'avg_sentiment': row[1],
                    'avg_intensity': row[2],
                    'dominant_emotions': json.loads(row[3]) if row[3] else [],
                    'total_interactions': row[4]
                })
            
            return trends
            
        except Exception as e:
            print(f"Error getting emotion trends: {e}")
            return []

    def search_memories(self, query, category=None, limit=10):
        """Search memories by text and category"""
        try:
            # Vector search
            query_embedding = self.sentence_model.encode(query).tolist()
            
            # Build where clause for category filter
            where_clause = {}
            if category:
                where_clause["category"] = category
            
            results = self.memory_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            memories = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    memories.append({
                        'content': doc,
                        'timestamp': metadata['timestamp'],
                        'user_input': metadata['user_input'],
                        'ai_response': metadata['ai_response'],
                        'category': metadata['category'],
                        'importance': metadata['importance']
                    })
            
            return memories
            
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []

    def get_memory_stats(self):
        """Get memory statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total memories
            cursor.execute('SELECT COUNT(*) FROM memories')
            total_memories = cursor.fetchone()[0]
            
            # Memories by category
            cursor.execute('''
                SELECT category, COUNT(*) 
                FROM memories 
                GROUP BY category 
                ORDER BY COUNT(*) DESC
            ''')
            category_counts = cursor.fetchall()
            
            # Average importance
            cursor.execute('SELECT AVG(importance_score) FROM memories')
            avg_importance = cursor.fetchone()[0] or 0
            
            # Recent activity (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute('SELECT COUNT(*) FROM memories WHERE timestamp > ?', (week_ago,))
            recent_activity = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_memories': total_memories,
                'category_distribution': dict(category_counts),
                'average_importance': round(avg_importance, 2),
                'recent_activity': recent_activity
            }
            
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {}

# Example usage and testing
if __name__ == "__main__":
    memory_manager = MemoryManager()
    
    print("Memory Manager initialized!")
    
    # Test saving a memory
    test_memory = {
        'timestamp': datetime.now().isoformat(),
        'user_input': "I'm really excited about my new job at the tech company!",
        'ai_response': "That's wonderful! I can feel your excitement. Tell me more about what you're looking forward to.",
        'emotion': {
            'sentiment': 'positive',
            'emotions': ['joy', 'excitement'],
            'intensity': 8
        }
    }
    
    memory_manager.save_memory(test_memory)
    
    # Test retrieving context
    context = memory_manager.get_relevant_context("work and career")
    print(f"Found {len(context)} relevant memories")
    
    # Test getting recent memories
    recent = memory_manager.get_recent_memories(5)
    print(f"Recent memories: {len(recent)}")
    
    # Test memory stats
    stats = memory_manager.get_memory_stats()
    print(f"Memory stats: {stats}")
