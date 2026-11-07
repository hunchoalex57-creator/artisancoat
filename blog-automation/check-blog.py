#!/usr/bin/env python3
"""
Artisan Coat — blog consistency check. Run before every publish:

    python3 blog-automation/check-blog.py

Exits non-zero if anything is wrong. It catches the problems that have
bitten this site before:
  * blog/posts.json entries whose HTML page does not exist (they render as
    404 cards on /blog/)
  * live posts missing from blog/posts.json (invisible on /blog/)
  * live posts missing from sitemap.xml
  * manifest categories that do not match a filter on blog/index.html
  * internal links (href/src) to files that do not exist, in every HTML page
  * manifest heroImage URLs on artisancoat.ca that point to missing files
"""
import json, os, re, sys
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
problems = []

def rel(p): return os.path.relpath(p, ROOT)

# --- manifest vs files ------------------------------------------------------
posts = json.load(open(os.path.join(ROOT, 'blog', 'posts.json'), encoding='utf-8'))
live = sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, 'blog'))
              if f.endswith('.html') and f != 'index.html')
slugs = [p['slug'] for p in posts]
for s in slugs:
    if s not in live:
        problems.append(f'manifest entry has no page: blog/{s}.html (move it to blog-automation/topics.json)')
for s in live:
    if s not in slugs:
        problems.append(f'live post missing from blog/posts.json: {s}')
if len(set(slugs)) != len(slugs):
    problems.append('duplicate slugs in blog/posts.json')

# --- categories vs index filters -------------------------------------------
index_html = open(os.path.join(ROOT, 'blog', 'index.html'), encoding='utf-8').read()
filters = set(re.findall(r'data-filter="([^"]+)"', index_html)) - {'all'}
for p in posts:
    if p.get('category') not in filters:
        problems.append(f"category '{p.get('category')}' on {p['slug']} matches no blog/index.html filter {sorted(filters)}")

# --- sitemap ----------------------------------------------------------------
sitemap = open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read()
in_sitemap = set(re.findall(r'blog/([a-z0-9-]+)\.html', sitemap))
for s in live:
    if s not in in_sitemap:
        problems.append(f'live post missing from sitemap.xml: blog/{s}.html')
for s in in_sitemap:
    if s != 'index' and s not in live:
        problems.append(f'sitemap.xml lists a page that does not exist: blog/{s}.html')

# --- hero images -------------------------------------------------------------
for p in posts:
    hi = p.get('heroImage', '')
    if hi.startswith('https://artisancoat.ca/'):
        if not os.path.exists(os.path.join(ROOT, hi[len('https://artisancoat.ca/'):])):
            problems.append(f'heroImage missing for {p["slug"]}: {hi}')

# --- internal links in every HTML page --------------------------------------
SKIP = ('http', 'mailto:', 'tel:', 'javascript:', 'data:', '//', '${')
for d, _, fs in os.walk(ROOT):
    if '/.git' in d or 'blog-automation' in d or 'blog-drafts' in d:
        continue
    for f in fs:
        if not f.endswith('.html'):
            continue
        fp = os.path.join(d, f)
        html = open(fp, encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'(?:href|src)="([^"#?]+)', html):
            h = m.group(1).strip()
            if not h or h.startswith(SKIP):
                continue
            target = os.path.join(ROOT, h.lstrip('/')) if h.startswith('/') else os.path.normpath(os.path.join(d, unquote(h)))
            if os.path.isdir(target):
                target = os.path.join(target, 'index.html')
            if not os.path.exists(target):
                problems.append(f'broken link in {rel(fp)}: {h}')
        for m in re.finditer(r'https://artisancoat\.ca/([^"\s#?]+\.html)', html):
            if not os.path.exists(os.path.join(ROOT, m.group(1))):
                problems.append(f'broken absolute link in {rel(fp)}: {m.group(0)}')

if problems:
    print(f'{len(problems)} problem(s):')
    for p in problems:
        print('  -', p)
    sys.exit(1)
print(f'OK: {len(live)} live posts, {len(posts)} manifest entries, {len(in_sitemap)} blog URLs in sitemap, no broken links.')
