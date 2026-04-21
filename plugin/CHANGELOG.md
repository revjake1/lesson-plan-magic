# Changelog

## 0.2.5

- Removed local Claude development settings from the release workflow and ignored `.claude/` / `.DS_Store`.
- Consolidated shared PII scanning vocabulary and matching logic into `shared/pii_common.py`.
- Clarified `--allow-names` help text and documented the `--skip-docx-scan` debugging flag.
- Replaced the private `ipaddress._BaseAddress` annotation in `safe_http.py`.
- Marked the sub-plan schema example's nearby-teacher sample as fictional.
