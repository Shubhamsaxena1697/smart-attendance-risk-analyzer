import json
import math
import os

DATA_FILE = "attendance_data.json"
MIN_REQUIRED = 75.0


def load_data():
    """Load saved attendance records from JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        print("Warning: Could not read saved data. Starting fresh.")
        return {}


def save_data(records):
    """Save attendance records to JSON file."""
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(records, file, indent=4)
    except IOError as e:
        print(f"Error saving data: {e}")


def get_valid_int(prompt):
    """Safely read a non-negative integer from the user."""
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("Please enter a non-negative number.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a whole number.")


def add_subject(records):
    """Add a new subject or overwrite an existing one."""
    subject = input("Enter subject name (e.g., Python, Calculus): ").strip().title()
    if not subject:
        print("Subject name cannot be empty.")
        return

    total = get_valid_int("Enter total classes held so far: ")
    attended = get_valid_int("Enter classes attended: ")

    if attended > total:
        print("Error: Attended classes cannot be more than total classes.")
        return

    records[subject] = {"attended": attended, "total": total}
    save_data(records)
    print(f"Saved '{subject}' ({attended}/{total}).")


def update_attendance(records):
    """Mark today's class as Present or Absent for an existing subject."""
    if not records:
        print("No subjects found. Add a subject first.")
        return

    print("\nAvailable Subjects:", ", ".join(records.keys()))
    subject = input("Enter subject name to update: ").strip().title()

    if subject not in records:
        print(f"Subject '{subject}' not found.")
        return

    status = input("Mark as Present (P) or Absent (A)? ").strip().upper()
    if status == "P":
        records[subject]["attended"] += 1
        records[subject]["total"] += 1
        print(f"Marked PRESENT for {subject}.")
    elif status == "A":
        records[subject]["total"] += 1
        print(f"Marked ABSENT for {subject}.")
    else:
        print("Invalid choice. Enter 'P' or 'A'.")
        return

    save_data(records)


def analyze_subject(attended, total):
    """
    Core computational feature:
    - Computes attendance percentage
    - Classifies risk status (SAFE / BORDERLINE / SHORTAGE)
    - Computes safe bunks available OR consecutive classes needed for 75%
    """
    if total == 0:
        return 0.0, "NO DATA", "No classes held yet."

    percentage = (attended / total) * 100

    if percentage >= 80.0:
        status = "SAFE"
    elif percentage >= MIN_REQUIRED:
        status = "BORDERLINE"
    else:
        status = "SHORTAGE"

    if percentage >= MIN_REQUIRED:
        # Max classes that can be skipped while staying >= 75%
        can_skip = math.floor((attended / 0.75) - total)
        advice = f"Can safely skip {can_skip} class(es)."
    else:
        # Consecutive classes needed to reach 75%
        needed = math.ceil((0.75 * total - attended) / 0.25)
        advice = f"Attend next {needed} class(es) continuously."

    return round(percentage, 2), status, advice


def view_report(records):
    """Display full attendance report sorted by lowest attendance first."""
    if not records:
        print("No subjects recorded yet.")
        return

    summary = []
    overall_attended = 0
    overall_total = 0

    for subject, data in records.items():
        att = data["attended"]
        tot = data["total"]
        overall_attended += att
        overall_total += tot
        pct, status, advice = analyze_subject(att, tot)
        summary.append((pct, subject, att, tot, status, advice))

    # Sort by percentage ascending so highest-risk subjects appear first
    summary.sort(key=lambda x: x[0])

    print("\n" + "=" * 78)
    print(f"{'SUBJECT':<18} {'ATT/TOT':<10} {'PERCENT':<10} {'STATUS':<12} {'RECOMMENDATION'}")
    print("=" * 78)
    for pct, subject, att, tot, status, advice in summary:
        print(f"{subject:<18} {f'{att}/{tot}':<10} {f'{pct}%':<10} {status:<12} {advice}")
    print("=" * 78)

    if overall_total > 0:
        overall_pct = round((overall_attended / overall_total) * 100, 2)
        print(f"OVERALL ATTENDANCE: {overall_attended}/{overall_total} ({overall_pct}%)")
    print("=" * 78)


def delete_subject(records):
    """Delete a subject from records."""
    if not records:
        print("No subjects to delete.")
        return

    print("\nAvailable Subjects:", ", ".join(records.keys()))
    subject = input("Enter subject name to delete: ").strip().title()
    if subject in records:
        del records[subject]
        save_data(records)
        print(f"Deleted '{subject}'.")
    else:
        print(f"Subject '{subject}' not found.")


def main():
    records = load_data()
    while True:
        print("\n--- STUDENT ATTENDANCE TRACKER & 75% CALCULATOR ---")
        print("1. Add / Set Subject")
        print("2. Mark Daily Attendance (P/A)")
        print("3. View Attendance Report & 75% Analysis")
        print("4. Delete Subject")
        print("5. Exit")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_subject(records)
        elif choice == "2":
            update_attendance(records)
        elif choice == "3":
            view_report(records)
        elif choice == "4":
            delete_subject(records)
        elif choice == "5":
            print("Goodbye! Stay above 75%.")
            break
        else:
            print("Invalid option. Please choose 1 to 5.")


if __name__ == "__main__":
    main()
