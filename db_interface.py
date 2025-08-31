import sqlite3
import os
from typing import Optional, Union

def make_connection(memory: bool = False, refresh: bool = False, db_path: str = "cookbook.db") -> sqlite3.Connection:
    """
    Create a SQLite database connection.
    
    Args:
        memory (bool): If True, use in-memory database. If False, use file-based database.
        refresh (bool): If True, remove existing database file before creating new connection.
        db_path (str): Path to the database file (ignored if memory=True).
    
    Returns:
        sqlite3.Connection: SQLite database connection
    """
    if memory:
        # In-memory database
        conn = sqlite3.connect(":memory:")
        print("Created in-memory SQLite database")
    else:
        # File-based database
        if refresh and os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        
        conn = sqlite3.connect(db_path)
        print(f"Connected to SQLite database: {db_path}")
    
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    
    return conn

def create_tables(conn: sqlite3.Connection) -> None:
    """
    Create basic tables for the cookbook application.
    
    Args:
        conn (sqlite3.Connection): Database connection
    """
    cursor = conn.cursor()
    
    # Create companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            ticker TEXT,
            sector TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create transcripts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            date TEXT NOT NULL,
            transcript_text TEXT,
            sentiment_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    """)
    
    # Create stock_prices table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            date TEXT NOT NULL,
            open_price REAL,
            close_price REAL,
            high_price REAL,
            low_price REAL,
            volume INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    """)
    
    conn.commit()
    print("Database tables created successfully")

def insert_company(conn: sqlite3.Connection, name: str, ticker: Optional[str] = None, sector: Optional[str] = None) -> int:
    """
    Insert a new company into the database.
    
    Args:
        conn (sqlite3.Connection): Database connection
        name (str): Company name
        ticker (str, optional): Stock ticker symbol
        sector (str, optional): Company sector
    
    Returns:
        int: ID of the inserted company
    """
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO companies (name, ticker, sector)
        VALUES (?, ?, ?)
    """, (name, ticker, sector))
    
    company_id = cursor.lastrowid
    conn.commit()
    print(f"Inserted company: {name} (ID: {company_id})")
    return company_id

def insert_transcript(conn: sqlite3.Connection, company_id: int, date: str, transcript_text: str, sentiment_score: Optional[float] = None) -> int:
    """
    Insert a new transcript into the database.
    
    Args:
        conn (sqlite3.Connection): Database connection
        company_id (int): ID of the company
        date (str): Date of the transcript
        transcript_text (str): Text content of the transcript
        sentiment_score (float, optional): Sentiment analysis score
    
    Returns:
        int: ID of the inserted transcript
    """
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transcripts (company_id, date, transcript_text, sentiment_score)
        VALUES (?, ?, ?, ?)
    """, (company_id, date, transcript_text, sentiment_score))
    
    transcript_id = cursor.lastrowid
    conn.commit()
    print(f"Inserted transcript for company ID {company_id} on {date}")
    return transcript_id

def get_companies(conn: sqlite3.Connection) -> list:
    """
    Get all companies from the database.
    
    Args:
        conn (sqlite3.Connection): Database connection
    
    Returns:
        list: List of company dictionaries
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies ORDER BY name")
    
    columns = [description[0] for description in cursor.description]
    companies = []
    
    for row in cursor.fetchall():
        companies.append(dict(zip(columns, row)))
    
    return companies

def get_transcripts(conn: sqlite3.Connection, company_id: Optional[int] = None) -> list:
    """
    Get transcripts from the database.
    
    Args:
        conn (sqlite3.Connection): Database connection
        company_id (int, optional): Filter by company ID
    
    Returns:
        list: List of transcript dictionaries
    """
    cursor = conn.cursor()
    
    if company_id:
        cursor.execute("""
            SELECT t.*, c.name as company_name 
            FROM transcripts t 
            JOIN companies c ON t.company_id = c.id 
            WHERE t.company_id = ?
            ORDER BY t.date DESC
        """, (company_id,))
    else:
        cursor.execute("""
            SELECT t.*, c.name as company_name 
            FROM transcripts t 
            JOIN companies c ON t.company_id = c.id 
            ORDER BY t.date DESC
        """)
    
    columns = [description[0] for description in cursor.description]
    transcripts = []
    
    for row in cursor.fetchall():
        transcripts.append(dict(zip(columns, row)))
    
    return transcripts 