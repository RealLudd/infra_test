"""
Simple Task Script - Modify this from Claude Mobile!
This script can be scheduled with Windows Task Scheduler
"""
from datetime import datetime
import time

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

def main():
    """Main task - modify the message below via Claude mobile!"""
    print_header()
    
    # === EDIT THIS MESSAGE FROM CLAUDE MOBILE! ===
    print("    >> wtf bro")
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

