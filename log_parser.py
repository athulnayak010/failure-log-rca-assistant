import re

def parse_log_file(filepath):
    """
    Reads a log file and extracts structured fields from each line.
    Expected format:
    [YYYY-MM-DD HH:MM:SS] TEST FAILED: test_name - ErrorType: error message
    """
    parsed_logs = []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pattern = re.compile(
        r"\[(?P<timestamp>[\d\-:\s]+)\]\s*TEST FAILED:\s*(?P<test_name>\S+)\s*-\s*(?P<error_type>\w+):\s*(?P<error_message>.+)"
    )

    for line_num, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue

        match = pattern.match(line)
        if match:
            parsed_logs.append({
                "line_number": line_num,
                "timestamp": match.group("timestamp").strip(),
                "test_name": match.group("test_name").strip(),
                "error_type": match.group("error_type").strip(),
                "error_message": match.group("error_message").strip(),
                "raw_line": line
            })
        else:
            # Handle noisy/unexpected format gracefully instead of crashing
            parsed_logs.append({
                "line_number": line_num,
                "timestamp": None,
                "test_name": None,
                "error_type": "UNPARSED",
                "error_message": line,
                "raw_line": line
            })

    return parsed_logs


# Quick manual test when running this file directly
if __name__ == "__main__":
    logs = parse_log_file("sample_logs.txt")
    print(f"Parsed {len(logs)} log lines\n")
    for log in logs[:3]:
        print(log)