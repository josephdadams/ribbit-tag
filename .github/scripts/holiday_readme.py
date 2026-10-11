"""Show the holiday map that's live today (or the next one coming) at the top of the README.

Reads each holiday map's dates straight from index.html, so the game and the README never disagree.
Run daily by .github/workflows/holiday-readme.yml; safe to run by hand too.
"""
import datetime, pathlib, re, sys
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[2]
HOLIDAYS = {'manor': 'Halloween', 'farm': 'Thanksgiving', 'santa': 'Christmas and New Year', 'valentine': "Valentine's Day",
            'rainbow': "St. Patrick's Day", 'eggs': 'Easter and spring', 'fireworks': 'Fourth of July'}
START, END = '<!-- HOLIDAY-MAP:START -->', '<!-- HOLIDAY-MAP:END -->'

def maps():
    src = (ROOT / 'index.html').read_text()
    pat = re.compile(r"\n  (\w+): \{\s*\n\s*label: (['\"])(.+?)\2, season: \[(\d+), (\d+)\], until: '([^']+)'")
    return [dict(key=m[1], label=m[3], start=int(m[4]), end=int(m[5]), until=m[6]) for m in pat.finditer(src)]

def live(mp, v):
    a, b = mp['start'], mp['end']
    return a <= v <= b if a <= b else (v >= a or v <= b)

def month_day(v):
    return datetime.date(2000, v // 100, v % 100).strftime('%b %-d')

def block(today):
    v = today.month * 100 + today.day
    ms = maps()
    if not ms: sys.exit('no holiday maps found in index.html')
    now = next((m for m in ms if live(m, v)), None)
    if now:
        head = f"### Now on the menu: {now['label']}"
        body = f"The {HOLIDAYS.get(now['key'], 'holiday')} map is available until {now['until']}. Look for it under **Limited time** on the map picker."
        m = now
    else:
        m = min(ms, key=lambda x: (x['start'] - v) % 1232)  # the next one to start
        head = f"### Coming next: {m['label']}"
        body = f"The {HOLIDAYS.get(m['key'], 'holiday')} map arrives on {month_day(m['start'])}."
    img = f"docs/screenshots/holiday-{m['key']}.png"
    pic = f"\n\n![{m['label']}]({img})" if (ROOT / img).exists() else ''
    return f"{START}\n{head}\n\n{body}{pic}\n{END}"

def main():
    today = datetime.datetime.now(ZoneInfo('America/New_York')).date()
    if len(sys.argv) > 1: today = datetime.date.fromisoformat(sys.argv[1])  # e.g. 2026-12-15, for testing
    readme = ROOT / 'README.md'
    text = readme.read_text()
    new = block(today)
    if START in text: text = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda _: new, text, flags=re.S)
    else: text = text.replace('### Holiday maps\n', '### Holiday maps\n\n' + new + '\n', 1)
    readme.write_text(text)
    print(new)

main()
