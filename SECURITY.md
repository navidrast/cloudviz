# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Code Scanning

CloudViz uses automated security scanning tools:

- **CodeQL**: Advanced semantic code analysis for Python
- **Bandit**: Python-specific security linter
- **Safety**: Python dependency vulnerability scanner
- **Semgrep**: Additional security pattern detection
- **Trivy**: Container image vulnerability scanning

### Manual Review Process

All security findings require **manual review** before resolution:

1. Security alerts are generated automatically
2. Maintainers review each alert for validity
3. Confirmed vulnerabilities are prioritized based on severity
4. Fixes are implemented through standard PR process
5. **No automatic commits or fixes are applied**

## Reporting a Vulnerability

### For Security Issues

If you discover a security vulnerability in CloudViz:

1. **DO NOT** open a public issue
2. Email us at: security@cloudviz.com (if available) or create a private security advisory
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Assessment**: Within 7 days
- **Fix Development**: Varies by severity
- **Public Disclosure**: After fix is released (coordinated disclosure)

### Severity Levels

- **Critical**: Remote code execution, data breach potential
- **High**: Privilege escalation, authentication bypass
- **Medium**: Denial of service, information disclosure
- **Low**: Minor security improvements

## Security Best Practices

### For Contributors

1. **Never commit secrets** (API keys, passwords, tokens)
2. **Use environment variables** for configuration
3. **Validate all inputs** to prevent injection attacks
4. **Follow secure coding practices** as outlined in CONTRIBUTING.md
5. **Review GitHub Copilot suggestions** for security implications

### For Users

1. **Keep CloudViz updated** to the latest version
2. **Use strong authentication** for cloud provider access
3. **Limit permissions** following principle of least privilege
4. **Monitor logs** for suspicious activity
5. **Use HTTPS** for all API communications

## Dependency Security

CloudViz regularly scans dependencies for known vulnerabilities:

- Python packages are checked with `safety`
- Container base images are scanned with `trivy`
- Updates are applied promptly for security issues

## Compliance

CloudViz follows security best practices for:

- OWASP Top 10 web application security risks
- CIS (Center for Internet Security) benchmarks
- Cloud security frameworks (AWS, Azure, GCP)

---

**Note**: This security policy applies to the CloudViz project. For security issues in cloud providers themselves, please contact the respective cloud provider's security team.