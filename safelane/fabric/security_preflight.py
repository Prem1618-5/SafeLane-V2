import re
import logging
from safelane.contracts import SecurityFinding

logger = logging.getLogger("safelane.fabric.security_preflight")

SECURITY_PENALTIES = {"info": 0, "warning": 8, "critical": 25}
MAX_SECURITY_PENALTY = 40

# Rule families (pure Python stdlib + regex, NO paid dependencies)
# 1. Secret exposure (critical) — vendor-specific token formats
SECRET_PATTERNS = [
    (r"-----BEGIN.*PRIVATE KEY-----", "Private key PEM block exposed"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub token exposed"),
    (r"sk-[a-zA-Z0-9]{20,}", "Secret key exposed (e.g. OpenAI)"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID exposed"),
    (r"xox[bpras]-[a-zA-Z0-9]+", "Slack token exposed"),
]

# 1b. Generic credential patterns — broader net, higher false-positive rate.
#     Deliberately separate so we can apply placeholder exclusion to these only.
GENERIC_SECRET_PATTERNS = [
    (r"(?i)(password|passwd|pwd)\s*[:=]\s*[\"']([^\"']{4,})[\"']", "Hardcoded password literal"),
    (r"(?i)(secret|api[_-]?key|access[_-]?key|credential)\s*[:=]\s*[\"']([^\"']{8,})[\"']", "Hardcoded secret/API key literal"),
    (r"(?i)(auth[_-]?token|bearer)\s*[:=]\s*[\"']([^\"']{8,})[\"']", "Hardcoded auth token literal"),
]

# Values that are unambiguously placeholders — skip these to reduce false positives
# on .env.example files, test fixtures, and documentation snippets.
PLACEHOLDER_VALUES = {
    "changeme", "change_me", "change-me",
    "xxx", "xxxx", "xxxxxxxx",
    "your-api-key-here", "your_api_key_here",
    "your-secret-here", "your_secret_here",
    "your-password-here", "your_password_here",
    "your-token-here", "your_token_here",
    "<password>", "<secret>", "<token>", "<api_key>",
    "placeholder", "example", "test", "dummy",
    "replace_me", "replace-me", "todo", "fixme",
}

# 2. CI/CD hardening (warning/critical)
CICD_CRITICAL_PATTERNS = [
    (r"permissions:\s*write-all", "Excessive CI/CD permissions (write-all)"),
    (r"pull_request_target(?:.|\n)*?checkout", "pull_request_target with checkout"),
]
CICD_WARNING_PATTERNS = [
    (r"uses:\s*[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+(?!\b[a-f0-9]{40}\b)", "Unpinned GitHub action (use commit SHA)"),
    (r"curl(?:.*)\|\s*(?:sh|bash)", "curl piped to shell"),
    (r"wget(?:.*)\|\s*(?:sh|bash)", "wget piped to shell"),
]

# 3. Code execution (warning)
CODE_EXEC_PATTERNS = [
    (r"eval\(", "Use of eval()"),
    (r"exec\(", "Use of exec()"),
    (r"subprocess\.(?:run|Popen|call|check_call|check_output)\([^)]*shell=True", "subprocess with shell=True"),
    (r"pickle\.loads\(", "Use of pickle.loads()"),
    (r"yaml\.load\((?!.*SafeLoader)", "yaml.load() without SafeLoader")
]

# 4. Transport/auth (warning)
TRANSPORT_PATTERNS = [
    (r"verify=False", "SSL verification disabled"),
    (r"--no-check-certificate", "SSL verification disabled in command"),
    (r"ssl\.CERT_NONE", "SSL certificate validation disabled"),
    (r"check_hostname\s*=\s*False", "Hostname verification disabled")
]

# 5. Prompt injection (warning)
PROMPT_INJECTION_PATTERNS = [
    (r"(?i)ignore previous instructions", "Potential prompt injection: 'ignore previous instructions'"),
    (r"(?i)you are now", "Potential prompt injection: 'you are now'"),
    (r"(?i)system:", "Potential prompt injection: 'system:'"),
    (r"<\|im_start\|>", "Potential prompt injection marker")
]

def run_preflight(diff: str, changed_files: list[str], pr_title: str = "", pr_body: str = "") -> list[SecurityFinding]:
    findings = []
    
    try:
        combined_text = f"{pr_title}\n{pr_body}\n{diff}"
        
        # 1. Secret exposure — vendor-specific (Critical)
        for pattern, rule_desc in SECRET_PATTERNS:
            if re.search(pattern, combined_text):
                findings.append(SecurityFinding(
                    rule_id="secret_exposure",
                    severity="critical",
                    file="multiple",
                    evidence=f"Redacted secret match found: {rule_desc}",
                    remediation="Remove the secret and rotate it immediately."
                ))

        # 1b. Secret exposure — generic credential patterns (Critical)
        #     These use a capturing group for the secret value so we can exclude
        #     known placeholder strings and reduce false positives.
        for pattern, rule_desc in GENERIC_SECRET_PATTERNS:
            match = re.search(pattern, combined_text)
            if match:
                # Group 2 is the captured secret value (the part inside quotes)
                captured_value = match.group(2).strip().lower()
                if captured_value not in PLACEHOLDER_VALUES:
                    findings.append(SecurityFinding(
                        rule_id="secret_exposure",
                        severity="critical",
                        file="multiple",
                        evidence=f"Redacted secret match found: {rule_desc}",
                        remediation="Remove the secret and rotate it immediately."
                    ))
        
        # 2. CI/CD Hardening
        for pattern, rule_desc in CICD_CRITICAL_PATTERNS:
            if re.search(pattern, combined_text):
                findings.append(SecurityFinding(
                    rule_id="cicd_hardening_critical",
                    severity="critical",
                    file="multiple",
                    evidence=rule_desc,
                    remediation="Restrict permissions or avoid dangerous workflow configurations."
                ))
        
        for pattern, rule_desc in CICD_WARNING_PATTERNS:
            if re.search(pattern, combined_text):
                findings.append(SecurityFinding(
                    rule_id="cicd_hardening_warning",
                    severity="warning",
                    file="multiple",
                    evidence=rule_desc,
                    remediation="Pin GitHub actions to a SHA or avoid piping curl/wget to sh."
                ))

        # 3. Code Execution (Warning)
        for pattern, rule_desc in CODE_EXEC_PATTERNS:
            if re.search(pattern, diff):
                findings.append(SecurityFinding(
                    rule_id="code_execution",
                    severity="warning",
                    file="multiple",
                    evidence=rule_desc,
                    remediation="Use safer alternatives for dynamic execution or deserialization."
                ))

        # 4. Transport/auth (Warning)
        for pattern, rule_desc in TRANSPORT_PATTERNS:
            if re.search(pattern, diff):
                findings.append(SecurityFinding(
                    rule_id="transport_auth",
                    severity="warning",
                    file="multiple",
                    evidence=rule_desc,
                    remediation="Enable SSL and hostname verification."
                ))

        # 5. Prompt Injection (Warning)
        for pattern, rule_desc in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, combined_text):
                findings.append(SecurityFinding(
                    rule_id="prompt_injection",
                    severity="warning",
                    file="multiple",
                    evidence=rule_desc,
                    remediation="Review inputs for prompt injection attempts."
                ))
                
    except Exception as e:
        logger.exception("Preflight scan crashed")
        findings.append(SecurityFinding(
            rule_id="preflight_crash",
            severity="warning",
            file="unknown",
            evidence="Security preflight scanner encountered an exception.",
            remediation="Check the scanner logs for errors."
        ))

    return findings



def apply_security_policy(score: int, findings: list[SecurityFinding]) -> tuple[int, bool]:
    penalty = min(MAX_SECURITY_PENALTY, sum(SECURITY_PENALTIES.get(f.severity, 0) for f in findings))
    final_score = max(0, score - penalty)
    has_critical = any(f.severity == "critical" for f in findings)
    return final_score, has_critical
