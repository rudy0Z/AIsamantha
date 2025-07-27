# scalable_memory.py - Advanced Memory Management with Complexity Handling
import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import logging

class ScalableMemoryManager:
    """Advanced memory system designed for long-term scalability"""
    
    def __init__(self, base_dir: str, max_active_memories: int = 50):
        self.base_dir = base_dir
        self.db_path = os.path.join(base_dir, "samantha_scalable_memory.db")
        self.max_active_memories = max_active_memories
        self.embedding_model = None
        
        # Memory management thresholds
        self.similarity_threshold = 0.4
        self.importance_decay_days = 30
        self.max_context_tokens = 2000
        
        self.init_database()
        self.load_embedding_model()
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for memory operations"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ScalableMemory")
    
    def load_embedding_model(self):
        """Load optimized embedding model"""
        try:
            print("Loading optimized sentence embedding model...")
            # Using smaller, faster model for production
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Embedding model loaded successfully")
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            self.embedding_model = None
    
    def init_database(self):
        """Initialize scalable database with optimization"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced conversations table with importance scoring
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                detected_emotion TEXT,
                importance_score REAL DEFAULT 1.0,
                access_count INTEGER DEFAULT 1,
                last_accessed TEXT,
                embedding BLOB,
                summary TEXT,
                session_id TEXT
            )
        ''')
        
        # Memory clusters for efficient retrieval
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cluster_label INTEGER,
                centroid_embedding BLOB,
                topic_summary TEXT,
                conversation_count INTEGER DEFAULT 0,
                last_updated TEXT
            )
        ''')
        
        # Conversation summaries for long-term memory
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                summary TEXT NOT NULL,
                key_emotions TEXT,
                important_events TEXT,
                conversation_count INTEGER
            )
        ''')
        
        # User profile for personalization
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY,
                name TEXT,
                communication_preferences TEXT,
                emotional_patterns TEXT,
                important_memories TEXT,
                relationship_milestones TEXT,
                last_updated TEXT
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_importance ON conversations(importance_score DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_emotion ON conversations(detected_emotion)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_count ON conversations(access_count DESC)')
        
        conn.commit()
        conn.close()
        print("Scalable memory database initialized with optimization")
    
    def calculate_importance_score(self, user_message: str, emotion: str, context: Dict = None) -> float:
        """Calculate importance score for memory prioritization"""
        base_score = 1.0
        
        # Emotional intensity scoring
        emotion_weights = {
            'joy': 1.5,      # Happy memories are important
            'sadness': 2.0,  # Emotional support moments
            'anger': 1.8,    # Conflict resolution
            'fear': 2.2,     # Anxiety support is crucial
            'surprise': 1.3,
            'neutral': 1.0
        }
        
        emotional_score = emotion_weights.get(emotion.lower(), 1.0)
        
        # Length and complexity scoring
        length_score = min(len(user_message.split()) / 20, 1.5)  # Longer = more important
        
        # Keywords that indicate important conversations
        important_keywords = [
            'love', 'relationship', 'family', 'death', 'job', 'career',
            'depression', 'anxiety', 'therapy', 'medication', 'crisis',
            'achievement', 'graduation', 'marriage', 'divorce', 'birth'
        ]
        
        keyword_score = 1.0
        for keyword in important_keywords:
            if keyword.lower() in user_message.lower():
                keyword_score += 0.3
        
        final_score = base_score * emotional_score * length_score * min(keyword_score, 2.5)
        return min(final_score, 5.0)  # Cap at 5.0
    
    def store_conversation_scalable(self, user_message: str, ai_response: str, emotion: str, session_id: str = None):
        """Store conversation with scalability optimizations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        importance = self.calculate_importance_score(user_message, emotion)
        
        # Generate embedding
        embedding = None
        if self.embedding_model:
            try:
                combined_text = f"{user_message} [emotion: {emotion}]"
                embedding_vector = self.embedding_model.encode(combined_text)
                embedding = embedding_vector.tobytes()
            except Exception as e:
                self.logger.error(f"Error generating embedding: {e}")
        
        # Create summary for long conversations
        summary = self.create_conversation_summary(user_message, ai_response)
        
        cursor.execute('''
            INSERT INTO conversations 
            (timestamp, user_message, ai_response, detected_emotion, importance_score, 
             last_accessed, embedding, summary, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, user_message, ai_response, emotion, importance, 
              timestamp, embedding, summary, session_id))
        
        conv_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Trigger cleanup if needed
        self.periodic_memory_cleanup()
        
        self.logger.info(f"💾 Stored conversation with importance {importance:.2f}")
        return conv_id
    
    def create_conversation_summary(self, user_msg: str, ai_response: str) -> str:
        """Create concise summary for long-term storage"""
        if len(user_msg) > 100:
            return f"User discussed: {user_msg[:100]}... | AI supported with emotional response"
        return f"User: {user_msg[:50]}... | AI: {ai_response[:50]}..."
    
    def retrieve_relevant_memories_scalable(self, current_message: str, emotion: str, limit: int = 10) -> List[Dict]:
        """Optimized memory retrieval with complexity management"""
        if not self.embedding_model:
            return self.get_recent_important_conversations(limit)
        
        try:
            # 1. Generate embedding for current message
            combined_text = f"{current_message} [emotion: {emotion}]"
            current_embedding = self.embedding_model.encode(combined_text)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 2. Smart filtering: Get top conversations by importance and recency
            cursor.execute('''
                SELECT id, user_message, ai_response, detected_emotion, timestamp, 
                       importance_score, access_count, embedding, summary
                FROM conversations 
                WHERE embedding IS NOT NULL 
                AND importance_score > 1.0
                AND datetime(timestamp) > datetime('now', '-90 days')
                ORDER BY importance_score DESC, access_count DESC
                LIMIT ?
            ''', (min(self.max_active_memories, 100),))
            
            conversations = cursor.fetchall()
            
            if not conversations:
                conn.close()
                return []
            
            # 3. Calculate similarities only for filtered set
            similarities = []
            for conv in conversations:
                if conv[7]:  # embedding exists
                    try:
                        stored_embedding = np.frombuffer(conv[7], dtype=np.float32)
                        similarity = cosine_similarity(
                            current_embedding.reshape(1, -1),
                            stored_embedding.reshape(1, -1)
                        )[0][0]
                        
                        # Boost similarity with importance and recency
                        importance_boost = conv[5] * 0.1  # importance_score boost
                        recency_boost = self.calculate_recency_boost(conv[4])  # timestamp boost
                        final_score = similarity + importance_boost + recency_boost
                        
                        similarities.append((final_score, conv))
                    except Exception as e:
                        self.logger.error(f"Error calculating similarity: {e}")
                        continue
            
            # 4. Sort and filter by threshold
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            relevant_memories = []
            for score, conv in similarities[:limit]:
                if score > self.similarity_threshold:
                    # Update access count for used memories
                    self.update_memory_access(conv[0])
                    
                    relevant_memories.append({
                        'id': conv[0],
                        'user_message': conv[1],
                        'ai_response': conv[2],
                        'emotion': conv[3],
                        'timestamp': conv[4],
                        'importance': conv[5],
                        'similarity_score': score,
                        'summary': conv[8]
                    })
            
            conn.close()
            self.logger.info(f"🔍 Retrieved {len(relevant_memories)} relevant memories (filtered from {len(conversations)})")
            return relevant_memories
            
        except Exception as e:
            self.logger.error(f"Error in scalable memory retrieval: {e}")
            return self.get_recent_important_conversations(limit)
    
    def calculate_recency_boost(self, timestamp: str) -> float:
        """Calculate recency boost for memory scoring"""
        try:
            conv_time = datetime.fromisoformat(timestamp)
            days_ago = (datetime.now() - conv_time).days
            
            if days_ago <= 1:
                return 0.3  # Very recent
            elif days_ago <= 7:
                return 0.2  # Recent
            elif days_ago <= 30:
                return 0.1  # Somewhat recent
            else:
                return 0.0  # Old
        except:
            return 0.0
    
    def update_memory_access(self, memory_id: int):
        """Update access count and timestamp for used memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE conversations 
            SET access_count = access_count + 1, last_accessed = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), memory_id))
        
        conn.commit()
        conn.close()
    
    def periodic_memory_cleanup(self):
        """Periodic cleanup to manage memory complexity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total conversation count
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_count = cursor.fetchone()[0]
        
        # If approaching memory limits, perform cleanup
        if total_count > 1000:  # Cleanup threshold
            self.logger.info("🧹 Starting memory cleanup process...")
            
            # 1. Archive old, low-importance conversations
            cutoff_date = (datetime.now() - timedelta(days=90)).isoformat()
            cursor.execute('''
                DELETE FROM conversations 
                WHERE timestamp < ? 
                AND importance_score < 1.5 
                AND access_count < 2
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            
            # 2. Create daily summaries for deleted conversations
            self.create_daily_summaries(conn, cutoff_date)
            
            conn.commit()
            self.logger.info(f"🧹 Cleaned up {deleted_count} old conversations")
        
        conn.close()
    
    def create_daily_summaries(self, conn, before_date: str):
        """Create daily summaries for long-term memory"""
        cursor = conn.cursor()
        
        # Group conversations by date and create summaries
        cursor.execute('''
            SELECT DATE(timestamp) as conv_date, 
                   GROUP_CONCAT(detected_emotion) as emotions,
                   COUNT(*) as conv_count
            FROM conversations 
            WHERE timestamp < ?
            GROUP BY DATE(timestamp)
        ''', (before_date,))
        
        daily_data = cursor.fetchall()
        
        for date, emotions, count in daily_data:
            emotion_list = emotions.split(',') if emotions else []
            dominant_emotion = max(set(emotion_list), key=emotion_list.count) if emotion_list else 'neutral'
            
            summary = f"Had {count} conversations. Dominant emotion: {dominant_emotion}"
            
            cursor.execute('''
                INSERT OR REPLACE INTO conversation_summaries 
                (date, summary, key_emotions, conversation_count)
                VALUES (?, ?, ?, ?)
            ''', (date, summary, emotions, count))
    
    def get_recent_important_conversations(self, limit: int = 10) -> List[Dict]:
        """Fallback: Get recent important conversations without embeddings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_message, ai_response, detected_emotion, timestamp, importance_score
            FROM conversations 
            ORDER BY importance_score DESC, timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        conversations = cursor.fetchall()
        conn.close()
        
        return [{
            'user_message': conv[0],
            'ai_response': conv[1],
            'emotion': conv[2],
            'timestamp': conv[3],
            'importance': conv[4]
        } for conv in conversations]
    
    def get_memory_statistics(self) -> Dict:
        """Get comprehensive memory statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Basic stats
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(importance_score) FROM conversations')
        avg_importance = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM conversations WHERE datetime(timestamp) > datetime("now", "-7 days")')
        recent_conversations = cursor.fetchone()[0]
        
        # Emotion distribution
        cursor.execute('''
            SELECT detected_emotion, COUNT(*) 
            FROM conversations 
            GROUP BY detected_emotion 
            ORDER BY COUNT(*) DESC
        ''')
        emotion_distribution = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_conversations': total_conversations,
            'average_importance': round(avg_importance, 2),
            'recent_conversations_7days': recent_conversations,
            'emotion_distribution': emotion_distribution,
            'memory_health': 'Good' if total_conversations < 1000 else 'Needs Cleanup'
        }
