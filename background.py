from datetime import datetime


def audit_log_transaction(action: str, userId: str):
    with open("audit_log.txt", "a") as file:
        content = f"{action} by user {userId} on {datetime.now()}"
        file.write(content + "\n")
