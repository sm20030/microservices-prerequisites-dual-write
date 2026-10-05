import sqlite3
import json
import time
import os

DB_FILE = "demo_outbox_simulation.db"

def setup_database():
    """Initializes a clean SQLite database for the simulation."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute("""
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            plan TEXT NOT NULL
        )
    """)
    
    # Create Outbox table
    cursor.execute("""
        CREATE TABLE outbox (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aggregate_type TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            processed TEXT DEFAULT 'FALSE'
        )
    """)
    
    # Seed a mock user
    cursor.execute("INSERT INTO users (id, email, plan) VALUES (?, ?, ?)", 
                   ("user-123", "founder@startup.com", "free"))
    
    conn.commit()
    conn.close()
    print(" [Setup] Initialized fresh SQLite database and seeded 'user-123' (Current Plan: free).\n")

def run_api_transaction(new_plan: str):
    """Simulates the API request handling an upgrade inside a single local transaction."""
    print("--- [STEP 1: API Request Received] ---")
    print(f"API attempting to upgrade user-123 to '{new_plan}'...")
    time.sleep(4.0)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Begin local ACID transaction
        cursor.execute("BEGIN TRANSACTION;")
        
        # 1. Update core application state
        cursor.execute("UPDATE users SET plan = ? WHERE id = ?", (new_plan, "user-123"))
        print("   -> [DB Write] Updated 'users' table successfully.")
        time.sleep(3.0)
        
        # 2. Write corresponding event to Outbox table in the SAME transaction
        event_payload = json.dumps({"user_id": "user-123", "new_plan": new_plan})
        cursor.execute("""
            INSERT INTO outbox (aggregate_type, event_type, payload) 
            VALUES (?, ?, ?)
        """, ("USER", "USER_PLAN_UPGRADED", event_payload))
        print("   -> [DB Write] Inserted event record into 'outbox' table atomically.")
        time.sleep(3.0)
        
        # Commit transaction (Both operations succeed together)
        conn.commit()
        print("✅ [Transaction Committed Successfully!]\n")
        time.sleep(3.0)
        
    except Exception as e:
        conn.rollback()
        print(f"❌ [Transaction Rolled Back due to error: {e}]")
    finally:
        conn.close()

def run_background_worker():
    """Simulates the background worker polling the Outbox table asynchronously."""
    print("--- [STEP 2: Background Worker Polling] ---")
    print("Worker looking for unprocessed outbox records...")
    time.sleep(4.0)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Query pending outbox records
    cursor.execute("SELECT id, event_type, payload FROM outbox WHERE processed = 'FALSE'")
    pending_events = cursor.fetchall()
    
    if not pending_events:
        print("   -> No pending events found in outbox.")
        conn.close()
        return

    for event_id, event_type, payload in pending_events:
        print(f"   -> [Found Outbox Event ID: {event_id}] Type: {event_type}")
        print(f"      Payload: {payload}")
        time.sleep(3.0)
        
        print("   -> [Network Dispatch] Publishing event to message broker (e.g., AWS SQS / Service Bus)...")
        time.sleep(5.0)
        print("      🚀 Event successfully delivered to downstream subscriber services!")
        
        # Mark record as processed
        cursor.execute("UPDATE outbox SET processed = 'TRUE' WHERE id = ?", (event_id,))
        conn.commit()
        print(f"   -> [State Update] Marked outbox record ID {event_id} as processed.\n")
        
    conn.close()
    print("✅ [Background Worker Cycle Complete]\n")

if __name__ == "__main__":
    os.system('clear' if os.name == 'posix' else 'cls')
    print("==================================================")
    print(" TRANSACTIONAL OUTBOX PATTERN: STEP-BY-STEP SIMULATION")
    print("==================================================\n")
    
    # 1. Setup DB
    setup_database()
    
    # 2. Simulate API request executing the local transaction
    run_api_transaction(new_plan="pro")
    
    # 3. Pause to highlight state gap
    print("⏳ [System Pause] API request finished and returned HTTP 200 to client.")
    print("   Data is safely committed locally, waiting for the background worker...\n")
    time.sleep(5.0)
    
    # 4. Simulate Background Worker picking up the event
    run_background_worker()
    
    print("==================================================")
    print(" SIMULATION FINISHED SUCCESSFULLY")
    print("==================================================")
