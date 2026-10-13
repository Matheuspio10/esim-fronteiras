import re, json, sys, time, html, urllib.request
from concurrent.futures import ThreadPoolExecutor
OUT = sys.argv[1]
MAX_ID = int(sys.argv[2])
UA = {"User-Agent": "Mozilla/5.0"}

def fetch(i):
    url = f"https://primera.e-sim.org/region.html?id={i}"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 500: return None
            time.sleep(2)
        except Exception:
            time.sleep(2)
    return "ERR"

def clean(s): return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()

def countries(block):
    return re.findall(r'xflagsSmall xflagsSmall-([\w\-]+)"></div>\s*<span class="countryNameTranslated">([^<]+)</span>', block)

def parse(i, t):
    m = re.search(r'<div class="regionContainer">(.*?)Travel and fight', t, re.S)
    if not m: return None
    head = m.group(1)
    name = clean(re.search(r'darkTableLookLikeHeader grid-col-1">(.*?)</div>', head, re.S).group(1))
    tiles = dict()
    for tm in re.finditer(r'<div class="regionInfoTile">\s*<div>(.*?)</div>\s*<div class="basicInfoFont">(.*?)</div>\s*</div>', head, re.S):
        tiles[clean(tm.group(1))] = tm.group(2)
    def own(k):
        c = countries(tiles.get(k, ""))
        return c[0][1] if c else None
    res_html = tiles.get("Resource", "")
    capital = None
    cm = re.search(r'Capital of\s*<div class="xflagsSmall xflagsSmall-([\w\-]+)"', res_html)
    if cm: capital = cm.group(1).replace("-", " ")
    def resource(h):
        r = re.search(r'title="([^"]+)"\s*src="[^"]*productIcons', h)
        lvl = re.search(r'<b style="color:[^"]*">\s*(\w+)\s*</b>', h)
        return (r.group(1) if r else None, lvl.group(1) if lvl else None)
    rname, rlvl = resource(res_html)
    pop = re.search(r'\d+', clean(tiles.get("Population", "")))
    neigh = []
    nm = re.search(r'Neighbour region</div>(.*?)(?:class="industryFlex"|$)', t, re.S)
    if nm:
        rows = re.split(r'<div class="d-grid grid-col-3', nm.group(1))[1:]
        for row in rows:
            a = re.search(r'region\.html\?id=(\d+)"[^>]*>([^<]+)</a>', row)
            if not a: continue
            nr, nl = resource(row)
            cs = countries(row)
            neigh.append({"id": int(a.group(1)), "name": html.unescape(a.group(2)).strip(), "res": nr, "lvl": nl,
                          "owner": cs[0][1] if cs else None, "rightful": cs[1][1] if len(cs) > 1 else None})
    return {"id": i, "name": name, "owner": own("Current owner"), "rightful": own("Rightful owner"),
            "capital": capital, "res": rname, "lvl": rlvl, "pop": int(pop.group()) if pop else None,
            "neighbors": neigh}

def job(i):
    t = fetch(i)
    if t is None: return i, None
    if t == "ERR": return i, "ERR"
    try: return i, parse(i, t)
    except Exception as e: return i, f"PARSEERR {e}"

regions, errs = [], []
with ThreadPoolExecutor(6) as ex:
    for i, r in ex.map(job, range(1, MAX_ID + 1)):
        if isinstance(r, dict): regions.append(r)
        elif r is not None: errs.append((i, r))
json.dump({"regions": regions, "errors": errs}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print(len(regions), "regions; errors:", errs[:10], "max id:", max(r["id"] for r in regions))
