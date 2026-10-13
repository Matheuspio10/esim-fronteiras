# Uso: python build.py <regions.json> <pos.json> <template.html> <saida.html> <data AAAA-MM-DD>
import json, sys
reg, pos, tpl, out, date = sys.argv[1:6]
d = json.load(open(reg, encoding="utf-8"))["regions"]
p = json.load(open(pos))
d.sort(key=lambda r: r["id"]); ix = {r["id"]: i for i, r in enumerate(d)}
regions = [[r["id"], r["name"], r["owner"], r["rightful"], r["capital"], r["res"], r["pop"], *p[str(r["id"])]] for r in d]
edges = sorted({tuple(sorted((ix[r["id"]], ix[n["id"]]))) for r in d for n in r["neighbors"]})
data = json.dumps({"date": date, "regions": regions, "edges": edges}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\/")
html = open(tpl, encoding="utf-8").read().replace("/*__DATA__*/null", data)
open(out, "w", encoding="utf-8").write(html)
print("ok", out, len(html) // 1024, "KB")
