"""
BPA Task Script - Runs silently every 20 seconds
Only shows popup when you activate it from mobile!
"""
from datetime import datetime
import time
import os

# ========================================
# CONTROL FLAG - EDIT THIS FROM MOBILE!
# ========================================
SHOW_MESSAGE = False  # Change to True to show popup
# ========================================

def print_header():
    """Print the BPA header with chicken ASCII art"""
    print("\n")
    print("    ========================================================")
    print("    ||                      B P A                        ||")
    print("    ========================================================")
    print("")
    print("                        ___")
    print("                    ___( o)>")
    print("                    \\ <_. )")
    print("                     `---'")
    print("")
    print("    ========================================================")
    print("")

def countdown(seconds):
    """Display a countdown timer"""
    print(f"    Closing in: ", end="", flush=True)
    for i in range(seconds, 0, -1):
        print(f"{i}...", end="", flush=True)
        time.sleep(1)
    print("0")
    print("")

def log_run():
    """Log each run to verify task is working"""
    log_file = "bpa_log.txt"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "POPUP SHOWN" if SHOW_MESSAGE else "SILENT RUN"
    
    try:
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] {status}\n")
    except:
        pass  # Ignore logging errors

def main():
    """Main task - runs every 20 seconds"""
    
    # Log this run
    log_run()
    
    # Only show popup if SHOW_MESSAGE is True
    if not SHOW_MESSAGE:
        # Silent mode - do nothing, just exit
        return
    
    # Show the message popup
    print_header()
    
    # === EDIT THIS MESSAGE FROM CLAUDE MOBILE! ===
    print("    >> Hello Marco - Message Activated!")
    # ==============================================
    
    print("")
    print(f"    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    print("    ========================================================")
    print("")
    
    # Countdown before closing
    countdown(10)

if __name__ == "__main__":
    main()

