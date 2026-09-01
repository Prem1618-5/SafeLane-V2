import unicodedata
from datetime import datetime
from safelane.contracts import PRPayload

MAX_DIFF_CHARS = 100_000
MAX_PATH_LENGTH = 500

def clean_untrusted_text(raw: str, max_length: int) -> str:
    """Strips null bytes, normalizes unicode NFKC, truncates."""
    if not isinstance(raw, str):
        return ""
    cleaned = raw.replace('\x00', '')
    normalized = unicodedata.normalize('NFKC', cleaned)
    return normalized[:max_length]

def normalize_pr_payload(raw: dict) -> PRPayload:
    """Safe defaults for missing keys, cap diff/paths."""
    if not isinstance(raw, dict):
        raw = {}
        
    diff_raw = str(raw.get("diff", ""))
    diff = clean_untrusted_text(diff_raw, MAX_DIFF_CHARS)
    
    changed_files = raw.get("changed_files", [])
    if not isinstance(changed_files, list):
        changed_files = []
    
    cleaned_files = []
    for f in changed_files:
        if isinstance(f, str):
            f_cleaned = clean_untrusted_text(f, MAX_PATH_LENGTH)
            if f_cleaned:
                cleaned_files.append(f_cleaned)
                
    timestamp = raw.get("timestamp")
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except Exception:
            timestamp = datetime.utcnow()
    elif not isinstance(timestamp, datetime):
        timestamp = datetime.utcnow()

    return PRPayload(
        pr_number=int(raw.get("pr_number", 0)),
        repo=str(raw.get("repo", "")),
        changed_files=cleaned_files,
        diff=diff,
        timestamp=timestamp,
        head_sha=str(raw.get("head_sha", "")) or None,
        skip_autofix=bool(raw.get("skip_autofix", False)),
    )
