"""
Simple Task Script - Modify this from Claude Mobile!
This script can be scheduled with Windows Task Scheduler
"""
from datetime import datetime
import time

def main():
    """Main task - modify the messages via Claude mobile!"""
    print("="*60)
    print(f"Task started at: {datetime.now()}")
    print("="*60)
    
    # These messages can be changed from Claude mobile!
    print("Hello from the scheduled task!")
    print("This message was last updated on: 2025-10-27")
    print("Status: Running automated task...")
    
    # Simulate some work
    print("\nProcessing...")
    time.sleep(2)
    
    # More messages you can modify
    print("Task completed successfully!")
    print("Next scheduled run: Check Task Scheduler")
    
    print("="*60)
    print(f"Task finished at: {datetime.now()}")
    print("="*60)

if __name__ == "__main__":
    main()

