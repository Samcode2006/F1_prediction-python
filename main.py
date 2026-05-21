# main.py
# F1 Race Winner Prediction System
# Entry point — runs the program and displays results

from predictor import load_drivers, predict_winner

# ──────────────────────────────────────────────
# DISPLAY HELPERS
# ──────────────────────────────────────────────

def print_banner():
    """Prints the welcome banner."""
    print("=" * 55)
    print("       🏎️  F1 RACE WINNER PREDICTION SYSTEM  🏁")
    print("=" * 55)


def print_rankings(ranked_drivers):
    """
    Prints all drivers ranked by predicted score in a
    clean, formatted table.

    Parameters:
        ranked_drivers (list of dict): sorted list from predict_winner()
    """
    print(f"\n{'Pos':<5} {'Driver':<15} {'Team':<15} {'Qual':<6} {'Prev':<6} {'Score':<6}")
    print("-" * 55)

    for i, driver in enumerate(ranked_drivers, start=1):
        # Add medal emoji for top 3
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"P{i} "

        print(
            f"{medal:<5} "
            f"{driver['Driver']:<15} "
            f"{driver['Team']:<15} "
            f"{driver['Qualifying']:<6} "
            f"{driver['PreviousFinish']:<6} "
            f"{driver['Score']:<6}"
        )


def print_winner(ranked_drivers):
    """
    Prints a highlighted prediction for the race winner.

    Parameters:
        ranked_drivers (list of dict): sorted list from predict_winner()
    """
    winner = ranked_drivers[0]
    print("\n" + "=" * 55)
    print("🏆  PREDICTED RACE WINNER")
    print("=" * 55)
    print(f"   Driver : {winner['Driver']}")
    print(f"   Team   : {winner['Team']}")
    print(f"   Score  : {winner['Score']} points")
    print("=" * 55)


def show_score_breakdown(ranked_drivers):
    """
    Shows how the score was broken down for each driver.
    Useful for understanding the prediction logic.

    Parameters:
        ranked_drivers (list of dict): sorted list from predict_winner()
    """
    print("\n📊  SCORE BREAKDOWN")
    print("-" * 55)

    for driver in ranked_drivers:
        qual_pts   = max(0, 11 - driver["Qualifying"])
        finish_pts = max(0, 11 - driver["PreviousFinish"])
        podium_pts = 5 if driver["PreviousFinish"] <= 3 else 0

        # Import TEAM_STRENGTH to show team score
        from predictor import TEAM_STRENGTH
        team_pts = TEAM_STRENGTH.get(driver["Team"], 3)

        print(f"\n  {driver['Driver']} ({driver['Team']})")
        print(f"    Qualifying bonus  : {qual_pts}")
        print(f"    Prev finish bonus : {finish_pts}")
        print(f"    Podium form bonus : {podium_pts}")
        print(f"    Team strength     : {team_pts}")
        print(f"    ─────────────────────")
        print(f"    TOTAL SCORE       : {driver['Score']}")


# ──────────────────────────────────────────────
# MENU
# ──────────────────────────────────────────────

def show_menu():
    """Prints the main menu and returns the user's choice."""
    print("\n📋  MAIN MENU")
    print("  1. Predict Race Winner")
    print("  2. Show Full Rankings")
    print("  3. Show Score Breakdown")
    print("  4. Exit")
    choice = input("\nEnter your choice (1-4): ").strip()
    return choice


# ──────────────────────────────────────────────
# MAIN PROGRAM
# ──────────────────────────────────────────────

def main():
    print_banner()

    # Load driver data from CSV once
    try:
        drivers = load_drivers("drivers.csv")
    except FileNotFoundError:
        print("\n❌ Error: 'drivers.csv' not found. Please make sure it's in the same folder.")
        return

    # Calculate and rank once (shared across menu options)
    ranked = predict_winner(drivers)

    # Menu loop
    while True:
        choice = show_menu()

        if choice == "1":
            print_winner(ranked)

        elif choice == "2":
            print("\n📋  FULL DRIVER RANKINGS")
            print("   (Qual = Grid Position | Prev = Last Race Finish)\n")
            print_rankings(ranked)

        elif choice == "3":
            show_score_breakdown(ranked)

        elif choice == "4":
            print("\n👋  Thanks for using F1 Predictor. See you at the next race!\n")
            break

        else:
            print("\n⚠️  Invalid choice. Please enter a number between 1 and 4.")


# Run the program
if __name__ == "__main__":
    main()
