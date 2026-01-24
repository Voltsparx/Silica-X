# core/help_menu.py

from core.colors import Colors, c

def show_help():
    print(c("\nSilica-X Help\n", Colors.BOLD + Colors.CYAN))

    print("• scan <username>   → Scan the username across platforms")
    print("• live <username>   → Launch live HTML dashboard for a username")
    print("• anonymity         → Configure Tor / Proxy anonymization")
    print("• clear             → Clear terminal screen")
    print("• help              → Show this help menu")
    print("• exit              → Quit Silica-X\n")
