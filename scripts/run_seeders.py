import os
from app.seeder import run_seeders

if __name__ == "__main__":
    # Optional: honor RESET_DB env var if set in environment
    # Example: os.environ["RESET_DB"] = "0"  # disable reset
    run_seeders()
