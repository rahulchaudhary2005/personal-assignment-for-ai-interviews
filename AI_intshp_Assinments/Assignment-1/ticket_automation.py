import pandas as pd
import re
from datetime import datetime, timedelta
import uuid

# ===============================
# 1. Load Ticket Dataset
# ===============================

data = pd.read_csv("tickets.csv")

# Lists to store results
processed_tickets = []
rejected_tickets = []

# Dictionary for duplicate detection
recent_tickets = {}

# ===============================
# 2. Validation Functions
# ===============================

def validate_email(email):
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(pattern, email)

def validate_priority(priority):
    return priority in ["Low", "Medium", "High"]

# ===============================
# 3. Routing Logic
# ===============================

def route_issue(issue):
    issue = issue.lower()

    routing = {
        "wifi": "Network Team",
        "login": "IT Support",
        "software": "Applications Team",
        "hardware": "Infrastructure Team",
        "other": "General Support"
    }

    return routing.get(issue, None)

# ===============================
# 4. SLA Calculation
# ===============================

def calculate_sla(priority, timestamp):

    time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")

    if priority == "High":
        return time + timedelta(hours=4)

    elif priority == "Medium":
        return time + timedelta(hours=24)

    elif priority == "Low":
        return time + timedelta(hours=72)

# ===============================
# 5. Process Tickets
# ===============================

for index, row in data.iterrows():

    name = row["Name"]
    email = row["Email"]
    issue = row["IssueType"].lower()
    priority = row["Priority"]
    description = row["Description"]
    timestamp = row["Timestamp"]

    # Validate Email
    if not validate_email(email):
        rejected_tickets.append([name, email, "Invalid Email"])
        continue

    # Validate Priority
    if not validate_priority(priority):
        rejected_tickets.append([name, email, "Invalid Priority"])
        continue

    # Duplicate Check (email + issue within 24h)
    key = email + "_" + issue
    time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")

    if key in recent_tickets:
        previous_time = recent_tickets[key]

        if (time - previous_time).total_seconds() < 86400:
            rejected_tickets.append([name, email, "Duplicate Ticket"])
            continue

    recent_tickets[key] = time

    # Generate Ticket ID
    ticket_id = "TICKET-" + str(uuid.uuid4())[:8]

    # Routing
    team = route_issue(issue)

    if team is None:
        rejected_tickets.append([name, email, "Unknown Issue Type"])
        continue

    # SLA
    sla_deadline = calculate_sla(priority, timestamp)

    # Save processed ticket
    processed_tickets.append([
        ticket_id,
        name,
        email,
        issue,
        priority,
        team,
        description,
        timestamp,
        sla_deadline
    ])

# ===============================
# 6. Convert to DataFrame
# ===============================

processed_df = pd.DataFrame(processed_tickets, columns=[
    "TicketID",
    "Name",
    "Email",
    "IssueType",
    "Priority",
    "AssignedTeam",
    "Description",
    "Timestamp",
    "SLA_Deadline"
])

rejected_df = pd.DataFrame(rejected_tickets, columns=[
    "Name",
    "Email",
    "Reason"
])

# ===============================
# 7. Save Output Files
# ===============================

processed_df.to_csv("processed_tickets.csv", index=False)
rejected_df.to_csv("rejected_tickets.csv", index=False)

# ===============================
# 8. Summary Report
# ===============================

summary = {
    "Total Tickets": len(data),
    "Processed Tickets": len(processed_df),
    "Rejected Tickets": len(rejected_df)
}

team_counts = processed_df["AssignedTeam"].value_counts()

summary_df = pd.DataFrame(list(summary.items()), columns=["Metric", "Value"])
team_df = team_counts.reset_index()
team_df.columns = ["Team", "Tickets"]

summary_df.to_csv("ticket_summary.csv", index=False)

print("Automation Completed")
print(summary_df)
print("\nTickets per Team")
print(team_df)