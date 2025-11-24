&lt;!-- -*- markdown -*- --&gt;
&lt;h1 align="center"&gt;
  &lt;br&gt;
  &lt;img src="docs/logo.png" alt="XSS-Hunter" width="120"&gt;
  &lt;br&gt;
  XSS-Hunter
  &lt;br&gt;
&lt;/h1&gt;

&lt;p align="center"&gt;
  &lt;a href="[https://github.com/thednato7m/your-xss-finder](https://github.com/Thednato7m/XSS_Finder)/actions"&gt;&lt;img src="https://github.com/thednato7m/your-xss-finder/workflows/CI/badge.svg" alt="CI"&gt;&lt;/a&gt;
  &lt;img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python"&gt;
  &lt;img src="https://img.shields.io/badge/licence-MIT-green.svg" alt="Licence"&gt;
  &lt;img src="https://img.shields.io/github/v/release/thednato7m/your-xss-finder?include_prereleases" alt="Release"&gt;
&lt;/p&gt;

**XSS-Hunter** is a one-command, open-source scanner that finds **Reflected**, **Stored** and **DOM-based** XSS while automatically riding common **WAF bypasses**.  
It uses a headless Chrome instance to confirm real JavaScript execution (`alert(1)` → `window.xss=1`) and minimise false positives.

---

## ⚡ Quick start
```bash
# 1. clone
git clone https://github.com/thednato7m/your-xss-finder.git
cd your-xss-finder

# 2. install
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. scan
python3 xss_hunter.py https://demo.testfire.net

📊 Sample output
Copy

[+] REFLECTED+DOM XSS  ->  https://demo.testfire.net/search?q=%27%3E%3Cscript%3Ewindow.xss%3D1%3C%2Fscript%3E
[+] STORED XSS         ->  https://demo.testfire.net/guestbook  payload='><svg/onload=window.xss=1>

🧰 Features

    Crawls & maps the target (depth-limited, domain-locked)
    Fuzzes every URL parameter, form field, header & cookie*
    Auto-mutates payloads to defeat naïve WAF rules (case, comment, protocol, back-tick, etc.)
    Re-uses Selenium/Chrome to execute the page and confirm window.xss=1
    Reports Reflected, Stored & DOM-based vectors in JSON and coloured CLI
    CI-friendly: zero-config GitHub Action included

* header/cookie fuzzing toggle coming in v1.1 – PRs welcome!
🚦 CLI flags
python3 xss_hunter.py https://example.com [--depth 3] [--cookies 'sess=abc'] [--auth-bearer TOKEN]
Table
Copy
Flag	Purpose
--depth	max crawl depth (default 2)
--cookies	semicolon-separated cookie string
--auth-bearer	JWT / API token
--json FILE	dump findings to JSON
--no-dom	skip heavy DOM checks (speed)
🧪 Test your build
bash
Copy

pytest -q -s

A disposable vulnerable app is spun up in CI so every push is automatically verified.
🤝 Contributing
Please read CONTRIBUTING.md – we love pull requests, issue reports and feature ideas.
📜 Licence
MIT – see LICENSE.
⚠️ Responsible usage
This tool is for authorised security testing only. Always obtain written permission before scanning any site you do not own.
<div align="center">
  🌟 Star the repo if it helped you – it keeps us motivated! 🌟
</div>
```
