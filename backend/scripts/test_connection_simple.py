"""
Simple database connection test following Supabase example
"""
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Parse DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"Testing connection to: {DATABASE_URL[:30]}...")

# Connect to the database
try:
    connection = psycopg2.connect(DATABASE_URL)
    print("✅ Connection successful!")
    
    # Create a cursor to execute SQL queries
    cursor = connection.cursor()
    
    # Example query
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print(f"✅ Current Time: {result}")
    
    # Check PostgreSQL version
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ PostgreSQL version: {version[0][:50]}...")
    
    # Check if pgvector extension exists
    cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
    has_pgvector = cursor.fetchone()
    if has_pgvector:
        print("✅ pgvector extension is installed")
    else:
        print("⚠️  pgvector extension not found!")

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("✅ Connection closed.")
    print("\n✅ All tests passed!")

except Exception as e:
    print(f"❌ Failed to connect: {e}")
