import re
import logging
from safelane.contracts import SecurityFinding

logger = logging.getLogger("safelane.fabric.security_preflight")

SECURITY_PENALTIES = {"info": 0, "warning": 8, "critical": 25}
MAX_SECURITY_PENALTY = 40

# Rule families (pure Python stdlib + regex, NO paid dependencies)
# 1. Secret exposure (critical) — vendor-specific token formats
SECRET_PATTERNS = [
    (r"-----BEGIN.*PRIVATE KEY-----", "Private key PEM block exposed", "https://cwe.mitre.org/data/definitions/798.html"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub token exposed", "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github"),
    (r"sk-[a-zA-Z0-9]{20,}", "Secret key exposed (e.g. OpenAI)", "https://cwe.mitre.org/data/definitions/798.html"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID exposed", "https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html"),
    (r"xox[bpras]-[a-zA-Z0-9]+", "Slack token exposed", "https://api.slack.com/authentication/token-types"),
]

# 1b. Generic credential patterns — broader net, higher false-positive rate.
#     Deliberately separate so we can apply placeholder exclusion to these only.
GENERIC_SECRET_PATTERNS = [
    (r"(?i)(password|passwd|pwd)\s*[:=]\s*[\"']([^\"']{4,})[\"']", "Hardcoded password literal", "https://cwe.mitre.org/data/definitions/259.html"),
    (r"(?i)(secret|api[_-]?key|access[_-]?key|credential)\s*[:=]\s*[\"']([^\"']{8,})[\"']", "Hardcoded secret/API key literal", "https://cwe.mitre.org/data/definitions/798.html"),
    (r"(?i)(auth[_-]?token|access[_-]?token|refresh[_-]?token|token|bearer)\s*[:=]\s*[\"']([^\"']{8,})[\"']", "Hardcoded auth/access/refresh/generic token literal", "https://cwe.mitre.org/data/definitions/798.html"),
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
    (r"permissions:\s*write-all", "Excessive CI/CD permissions (write-all)", "https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions"),
    (r"pull_request_target(?:.|\n)*?checkout", "pull_request_target with checkout", "https://securitylab.github.com/research/github-actions-preventing-pwn-requests/"),
]
CICD_WARNING_PATTERNS = [
    (r"uses:\s*[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+(?!\b[a-f0-9]{40}\b)", "Unpinned GitHub action (use commit SHA)", "https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions#using-third-party-actions"),
    (r"curl(?:.*)\|\s*(?:sh|bash)", "curl piped to shell", "https://cwe.mitre.org/data/definitions/78.html"),
    (r"wget(?:.*)\|\s*(?:sh|bash)", "wget piped to shell", "https://cwe.mitre.org/data/definitions/78.html"),
]

# 3. Code execution (warning)
CODE_EXEC_PATTERNS = [
    (r"eval\(", "Use of eval()", "https://cwe.mitre.org/data/definitions/95.html"),
    (r"exec\(", "Use of exec()", "https://cwe.mitre.org/data/definitions/95.html"),
    (r"subprocess\.(?:run|Popen|call|check_call|check_output)\([^)]*shell=True", "subprocess with shell=True", "https://cwe.mitre.org/data/definitions/78.html"),
    (r"pickle\.loads\(", "Use of pickle.loads()", "https://cwe.mitre.org/data/definitions/502.html"),
    (r"yaml\.load\((?!.*SafeLoader)", "yaml.load() without SafeLoader", "https://cwe.mitre.org/data/definitions/502.html")
]

# 4. Transport/auth (warning)
TRANSPORT_PATTERNS = [
    (r"verify=False", "SSL verification disabled", "https://cwe.mitre.org/data/definitions/295.html"),
    (r"--no-check-certificate", "SSL verification disabled in command", "https://cwe.mitre.org/data/definitions/295.html"),
    (r"ssl\.CERT_NONE", "SSL certificate validation disabled", "https://cwe.mitre.org/data/definitions/295.html"),
    (r"check_hostname\s*=\s*False", "Hostname verification disabled", "https://cwe.mitre.org/data/definitions/297.html")
]

# 5. Prompt injection (warning)
PROMPT_INJECTION_PATTERNS = [
    (r"(?i)ignore previous instructions", "Potential prompt injection: 'ignore previous instructions'", "https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-2023-v1_1.pdf"),
    (r"(?i)you are now", "Potential prompt injection: 'you are now'", "https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-2023-v1_1.pdf"),
    (r"(?i)system:", "Potential prompt injection: 'system:'", "https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-2023-v1_1.pdf"),
    (r"<\|im_start\|>", "Potential prompt injection marker", "https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-2023-v1_1.pdf")
]

def run_preflight(diff: str, changed_files: list[str], pr_title: str = "", pr_body: str = "") -> list[SecurityFinding]:
    findings = []
    
    try:
        combined_text = f"{pr_title}\n{pr_body}\n{diff}"
        
        # 1. Secret exposure — vendor-specific (Critical)
        for pattern, rule_desc, ref_url in SECRET_PATTERNS:
            if re.search(pattern, combined_text):
                findings.append(SecurityFinding(
                    rule_id="secret_exposure",
                    severity="critical",
                    file="multiple",
                    evidence=f"Redacted secret match found: {rule_desc}",
                    remediation="Remove the secret and rotate it immediately.",
                    reference=ref_url
                ))

        # 1b. Secret exposure — generic credential patterns (Critical)
        #     These use a capturing group for the secret value so we can exclude
        #     known placeholder strings and reduce false positives.
        for pattern, rule_desc, ref_url in GENERIC_SECRET_PATTERNS:
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
                        remediation="Remove the secret and rotate it immediately.",
                        reference=ref_url
                    ))
        
        # 2. CI/CD Hardening
        for pattern, rule_desc, ref_url in CICD_CRITICAL_PATTERNS:
            if re.search(pattern, combined_text):
                findings.append(SecurityFinding(
                    rule_id="cicd_hardening_critical",
                    severity="critical",
                    file="multiple",
                    evidence=rule_desc,
                    remediation="Restrict permissions or avoid dangerous workflow configurations.",
                    reference=ref_url
                ))
        
        for pattern, rule_desc, ref_url in CICD_WARNING_PATTERNS:
            if re.search(pattern, combined_text):
                findings.append(SecurityFinding(
                    rule_id="cicd_hardening_warning",
                    severity="warning",
                    file="multiple",
                    evidence=rule_desc,
                    remediation="Pin GitHub actions to a SHA or avoid piping curl/wget to sh.",
                    reference=ref_url
                ))

        # 3. Code Execution (Warning)
        for pattern, rule_desc, ref_url in CODE_EXEC_PATTERNS:
            if re.search(pattern, diff):
                findings.append(SecurityFinding(
                    rule_id="code_execution",
                    severity="warning",
                    file="multiple",
                    evidence=rule_desc,
                    remediation="Use safer alternatives for dynamic execution or deserialization.",
                    reference=ref_url
                ))

        # 4. Transport/auth (Warning)
        for pattern, rule_desc, ref_url in TRANSPORT_PATTERNS:
            if re.search(pattern, diff):
                findings.append(SecurityFinding(
                    rule_id="transport_auth",
                    severity="warning",
                    file="multiple",
                    evidence=rule_desc,
                    remediation="Enable SSL and hostname verification.",
                    reference=ref_url
                ))

        # 5. Prompt Injection (Warning)
        for pattern, rule_desc, ref_url in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, combined_text):
                findings.append(SecurityFinding(
                    rule_id="prompt_injection",
                    severity="warning",
                    file="multiple",
                    evidence=rule_desc,
                    remediation="Review inputs for prompt injection attempts.",
                    reference=ref_url
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
