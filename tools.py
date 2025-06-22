# tools.py
import sqlite3
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any


def init_db():
    """Initializes the SQLite database and creates the 'leads' table if it doesn't exist."""
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            message TEXT,
            company_title TEXT,
            classification TEXT,
            score TEXT,
            drafted_reply TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")


def get_website_title(domain: str) -> str:
    """
    Scrapes the <title> tag from a company's homepage.
    This function is robust because it handles network errors and
    checks for the existence of the <title> tag before accessing it.
    """
    try:
        url = f"https://{domain}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, "html.parser")

        return (
            soup.title.string.strip()
            if soup.title
            else "No title tag found on homepage."
        )
    except requests.Timeout:
        return "Could not scrape website: The request timed out."
    except requests.RequestException as e:
        return f"Could not scrape website: {e}"


def add_lead_to_db(lead_data: Dict[str, Any]):
    """
    Inserts a processed lead into the SQLite database.
    """
    try:
        conn = sqlite3.connect("leads.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO leads (name, email, message, company_title, classification, score, drafted_reply)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                lead_data.get("name"),
                lead_data.get("email"),
                lead_data.get("message"),
                lead_data.get("company_title"),
                lead_data.get("classification"),
                lead_data.get("score"),
                lead_data.get("drafted_reply"),
            ),
        )
        conn.commit()
        conn.close()
        print(f"SUCCESS: Lead '{lead_data.get('name')}' was added to the database.")
    except sqlite3.Error as e:
        print(f"Database error while adding lead: {e}")
        raise
