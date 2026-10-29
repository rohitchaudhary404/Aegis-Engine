import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "assessment_engine.db"):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        """Returns a connection with WAL mode enabled for better concurrency."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes the database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Concept Families Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS concept_families (
                    family_id TEXT PRIMARY KEY,
                    section TEXT NOT NULL,
                    sub_topic TEXT NOT NULL,
                    structural_schema TEXT
                )
            ''')
            
            # Items Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    item_id TEXT PRIMARY KEY,
                    family_id TEXT,
                    stem TEXT NOT NULL,
                    options TEXT NOT NULL, -- JSON array
                    correct_answer TEXT NOT NULL,
                    empirical_p_value REAL,
                    irt_difficulty_b REAL,
                    irt_discrimination_a REAL,
                    point_biserial REAL,
                    approval_status TEXT DEFAULT 'DRAFT', -- DRAFT, APPROVED, REJECTED
                    is_quarantined BOOLEAN DEFAULT 0,
                    vector_embedding BLOB, -- Serialized numpy array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(family_id) REFERENCES concept_families(family_id)
                )
            ''')
            
            # Response Logs Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS response_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_source TEXT NOT NULL, -- e.g., IMAP_BASELINE, PILOT, SLOT_1
                    candidate_id TEXT NOT NULL,
                    slot_id INTEGER,
                    item_id TEXT NOT NULL,
                    is_correct BOOLEAN NOT NULL,
                    response_time_sec REAL,
                    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(item_id) REFERENCES items(item_id)
                )
            ''')
            
            # Slot Forms Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS slot_forms (
                    form_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slot_id INTEGER NOT NULL,
                    item_id TEXT NOT NULL,
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(item_id) REFERENCES items(item_id),
                    UNIQUE(slot_id, item_id)
                )
            ''')
            
            # Leak Alerts Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leak_alerts (
                    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL, -- CUSUM, OSINT
                    item_id TEXT NOT NULL,
                    evidence_payload TEXT, -- JSON details
                    hot_swap_item_id TEXT, -- Replacement item
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(item_id) REFERENCES items(item_id)
                )
            ''')
            
            conn.commit()
            logger.info("Database schema initialized successfully.")

    # Utility functions for basic operations
    def insert_concept_family(self, family_id: str, section: str, sub_topic: str, structural_schema: str = ""):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR IGNORE INTO concept_families (family_id, section, sub_topic, structural_schema)
                VALUES (?, ?, ?, ?)
            ''', (family_id, section, sub_topic, structural_schema))
            conn.commit()

    def insert_item(self, item_data: Dict[str, Any]):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO items (
                    item_id, family_id, stem, options, correct_answer, 
                    empirical_p_value, irt_difficulty_b, irt_discrimination_a, 
                    point_biserial, approval_status, is_quarantined
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item_data.get('item_id'), item_data.get('family_id'), item_data.get('stem'),
                json.dumps(item_data.get('options', [])), item_data.get('correct_answer'),
                item_data.get('empirical_p_value'), item_data.get('irt_difficulty_b'),
                item_data.get('irt_discrimination_a'), item_data.get('point_biserial'),
                item_data.get('approval_status', 'DRAFT'), item_data.get('is_quarantined', False)
            ))
            conn.commit()

