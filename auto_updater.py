"""
Auto-Updater Script
Automatically pulls latest code from GitHub and restarts if changes detected
"""
import subprocess
import sys
import time
import os
from datetime import datetime

def git_pull():
    """
    Pull latest changes from GitHub.
    Returns True if updates were found, False otherwise.
    """
    try:
        result = subprocess.run(
            ['git', 'pull'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Check if there were updates
        if 'Already up to date' in result.stdout:
            return False
        elif 'Updating' in result.stdout or 'Fast-forward' in result.stdout:
            print(f"[{datetime.now()}] ✅ New code pulled from GitHub!")
            print(result.stdout)
            return True
        else:
            print(f"[{datetime.now()}] Git pull output: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error pulling from GitHub: {e}")
        return False

def restart_script(script_name):
    """Restart the target script with updated code"""
    print(f"[{datetime.now()}] 🔄 Restarting {script_name} with new code...")
    subprocess.Popen([sys.executable, script_name])

def main():
    """
    Main auto-update loop
    """
    TARGET_SCRIPT = "automation_example.py"  # Script to monitor and restart
    CHECK_INTERVAL = 60  # Check for updates every 60 seconds
    
    print("="*60)
    print("🤖 Auto-Updater Started")
    print("="*60)
    print(f"📂 Monitoring: {TARGET_SCRIPT}")
    print(f"⏱️  Check interval: {CHECK_INTERVAL} seconds")
    print(f"🔗 Watching GitHub for changes...")
    print("="*60)
    print()
    
    while True:
        try:
            # Check for updates from GitHub
            if git_pull():
                print(f"[{datetime.now()}] 🚀 Changes detected!")
                print(f"[{datetime.now()}] ℹ️  New code is now active.")
                print(f"[{datetime.now()}] ℹ️  If {TARGET_SCRIPT} is running,")
                print(f"                       restart it to use the new code.")
                print()
            else:
                print(f"[{datetime.now()}] ✓ No updates. Code is up to date.")
            
            # Wait before next check
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] ⛔ Auto-updater stopped by user")
            break
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()

