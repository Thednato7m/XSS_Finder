

**XSS-Finder** is a one-command, open-source scanner that finds **Reflected**, **Stored** and **DOM-based** XSS while automatically riding common **WAF bypasses**.  
It uses a headless Chrome instance to confirm real JavaScript execution (`alert(1)` → `window.xss=1`) and minimise false positives.

---

## ⚡ Quick start
```bash
# 1. clone
git clone https://github.com/YOUR_USER/your-xss-finder.git
cd your-xss-finder

# 2. install
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. scan
python3 xss_hunter.py https://demo.testfire.net
