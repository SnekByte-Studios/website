import time
from CRUD import CRUD

def cleanup_expired_sessions():
    db = CRUD()
    sessions = db.read("sessions", "sessions")
    now = int(time.time())
    expiration_seconds = 1800

    expired_count = 0
    for session_id, token, timestamp in sessions:
        if now - int(timestamp) > expiration_seconds:
            print(f"Deleting expired session: ID={session_id}, Time={timestamp}")
            db.delete("sessions", "sessions", "ID", session_id)
            expired_count += 1

    print(f"Cleanup complete. {expired_count} expired session(s) deleted.")

if __name__ == "__main__":
    cleanup_expired_sessions()
