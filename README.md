

**XSS-Finder** is a one-command, open-source scanner that finds **Reflected**, **Stored** and **DOM-based** XSS while automatically riding common **WAF bypasses**.  
It uses a headless Chrome instance to confirm real JavaScript execution (`alert(1)` → `window.xss=1`) and minimise false positives.

---

## ⚡ Quick start
```bash
# 1. clone
git clone https://github.com/YOUR_USER/your-xss-finder.git
cd xss-finder

# 2. install
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. scan
python3 xss_finder.py https://demo.testfire.net

🧰 Features

    Crawls & maps the target (depth-limited, domain-locked)
    Fuzzes every URL parameter, form field, header & cookie*
    Auto-mutates payloads to defeat naïve WAF rules (case, comment, protocol, back-tick, etc.)
    Re-uses Selenium/Chrome to execute the page and confirm window.xss=1
    Reports Reflected, Stored & DOM-based vectors in JSON and coloured CLI
    CI-friendly: zero-config GitHub Action included
