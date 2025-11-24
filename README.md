&lt;!-- -*- markdown -*- --&gt;
&lt;h1 align="center"&gt;
  &lt;br&gt;
  &lt;img src="docs/logo.png" alt="XSS-Hunter" width="120"&gt;
  &lt;br&gt;
  XSS-Hunter
  &lt;br&gt;
&lt;/h1&gt;

&lt;p align="center"&gt;
  &lt;a href="https://github.com/YOUR_USER/your-xss-finder/actions"&gt;&lt;img src="https://github.com/YOUR_USER/your-xss-finder/workflows/CI/badge.svg" alt="CI"&gt;&lt;/a&gt;
  &lt;img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python"&gt;
  &lt;img src="https://img.shields.io/badge/licence-MIT-green.svg" alt="Licence"&gt;
  &lt;img src="https://img.shields.io/github/v/release/YOUR_USER/your-xss-finder?include_prereleases" alt="Release"&gt;
&lt;/p&gt;

**XSS-Hunter** is a one-command, open-source scanner that finds **Reflected**, **Stored** and **DOM-based** XSS while automatically riding common **WAF bypasses**.  
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
