"""
Example Automation Script
This demonstrates a non-web automation that can be modified via mobile
"""
import time
from datetime import datetime

def check_system_health():
    """Check system health metrics"""
    print(f"[{datetime.now()}] Checking system health...")
    # Add your monitoring logic here
    cpu_usage = 45  # Example
    memory_usage = 67  # Example
    print(f"  CPU: {cpu_usage}%")
    print(f"  Memory: {memory_usage}%")
    return cpu_usage, memory_usage

def send_alert(message):
    """Send alert notification"""
    print(f"🚨 ALERT: {message}")
    # Add your notification logic (email, Slack, etc.)

def main():
    """Main automation loop"""
    print("="*60)
    print("🤖 Automation Script Started")
    print("="*60)
    
    # Thresholds (can be modified via Claude mobile!)
    CPU_THRESHOLD = 80
    MEMORY_THRESHOLD = 85
    
    while True:
        cpu, memory = check_system_health()
        
        # Alert if thresholds exceeded
        if cpu > CPU_THRESHOLD:
            send_alert(f"High CPU usage: {cpu}%")
        
        if memory > MEMORY_THRESHOLD:
            send_alert(f"High memory usage: {memory}%")
        
        print(f"  Status: OK (Next check in 60 seconds)")
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ Automation stopped by user")

