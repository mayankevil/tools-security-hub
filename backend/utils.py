from datetime import datetime, timedelta

def deduplicate_findings(findings):
    seen = set()
    unique = []
    for f in findings:
        key = (f['Resources'][0]['Id'], f['Title'])
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique