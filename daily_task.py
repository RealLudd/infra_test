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
    print("                       _/~\\_")
    print("                      ( o.o )")
    print("                       > ^ <")
    print("                    /|      |\\")
    print("                   / |      | \\")
    print("                  /  |      |  \\")
    print("                 /   ========   \\")
    print("")
    print("    ========================================================")
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
    
    # Keep window open for 10 seconds
    time.sleep(10)

if __name__ == "__main__":
    main()

