"""IT helpdesk ticket allocator: raise, assign, note, close and save tickets."""
import hmac
import itertools
import json
import os
import re
import shutil
import subprocess  # nosec B404 - used without a shell, input validated
from datetime import datetime

tickets = {}
TICKET_IDS = itertools.count(101)
HOSTNAME_RE = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9.-]{0,251}[A-Za-z0-9])?$")


def parse_urgency(urgency):
    """Convert urgency to an int and make sure it is between 1 and 5."""
    value = int(urgency)
    if not 1 <= value <= 5:
        raise ValueError(f"urgency must be between 1 and 5, got {value}")
    return value


def raise_ticket(user, issue_type, urgency="3", audit_trail=None):
    """Create a ticket and return its id."""
    if audit_trail is None:
        audit_trail = []
    priority = parse_urgency(urgency)
    ticket_id = next(TICKET_IDS)
    tickets[ticket_id] = {
        "user": user,
        "issue": issue_type,
        "priority": priority,
        "tech": None,
        "notes": [],
    }
    audit_trail.append(f"{user} raised #{ticket_id} at {datetime.now()}")
    return ticket_id


def assign_ticket(ticket_id, technician):
    """Assign a technician to a ticket."""
    tickets[ticket_id]["tech"] = technician


def add_note(ticket_id, note):
    """Add a note to a ticket; return False if the ticket does not exist."""
    try:
        tickets[ticket_id]["notes"].append(note)
    except KeyError:
        print(f"Cannot add note: ticket #{ticket_id} not found")
        return False
    return True


def close_ticket(ticket_id, password):
    """Close a ticket if the admin password is correct."""
    admin_password = os.environ.get("HELPDESK_ADMIN_PASSWORD", "")
    if not admin_password or not hmac.compare_digest(
            password.encode(), admin_password.encode()):
        print("Access denied: ticket not closed")
        return False
    if ticket_id not in tickets:
        print(f"Cannot close: ticket #{ticket_id} not found")
        return False
    del tickets[ticket_id]
    return True


def unresolved_high_priority():
    """Return ids of tickets with priority >= 4 and no technician."""
    result = []
    for ticket_id, ticket in tickets.items():
        if ticket["priority"] >= 4 and ticket["tech"] is None:
            result.append(ticket_id)
    return result


def ping_user_machine(hostname):
    """Ping a host once and return the exit code (no shell is used)."""
    if not HOSTNAME_RE.match(hostname):
        raise ValueError(f"invalid hostname: {hostname!r}")
    ping = shutil.which("ping")
    if ping is None:
        raise FileNotFoundError("ping command not found")
    count_flag = "-n" if os.name == "nt" else "-c"
    return subprocess.run(  # nosec B603
        [ping, count_flag, "1", hostname], check=False
    ).returncode


def save_tickets(file="tickets.json"):
    """Write all tickets to a JSON file."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(tickets, handle)


def main():
    """Run the demo workflow."""
    t1 = raise_ticket("anil", "printer", "5")
    t2 = raise_ticket("meera", "wifi", "4")
    try:
        raise_ticket("joe", "vpn", "-7")
    except ValueError as err:
        print("Rejected ticket:", err)
    assign_ticket(t1, "Tech-Kiran")
    add_note(999, "Called user")
    print("Unassigned high priority:", unresolved_high_priority())
    level = input("Urgency for a new laptop ticket (1-5, Enter for 3): ")
    try:
        raise_ticket("sana", "laptop", level or "3")
    except ValueError as err:
        print("Rejected ticket:", err)
    close_ticket(t2, os.environ.get("HELPDESK_ADMIN_PASSWORD", ""))
    save_tickets()
    print("Open tickets:", list(tickets.keys()))


if __name__ == "__main__":
    main()
