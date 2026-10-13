# Atualiza os dados (donos mudam com as guerras) e regera o site (index.html).
# Uso:
#   python atualizar.py             -> coleta de novo (~6 min) e regera o index.html localmente
#   python atualizar.py --publicar  -> faz o mesmo e envia para o GitHub (o site atualiza em ~1 min)
# As posições do mapa (dados/pos.json) são reaproveitadas; só recalcula se surgirem regiões novas.
import subprocess, sys, json, os, datetime
B = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(B, "scripts"); Dd = os.path.join(B, "dados")
reg, pos = os.path.join(Dd, "regions.json"), os.path.join(Dd, "pos.json")
hoje = datetime.date.today().isoformat()
subprocess.check_call([sys.executable, "-I", os.path.join(S, "scrape.py"), reg, "1200"])
ids = {str(r["id"]) for r in json.load(open(reg, encoding="utf-8"))["regions"]}
if not os.path.exists(pos) or not ids <= set(json.load(open(pos))):
    subprocess.check_call([sys.executable, "-I", os.path.join(S, "layout.py"), reg, pos])
subprocess.check_call([sys.executable, "-I", os.path.join(S, "build.py"), reg, pos, os.path.join(S, "template.html"),
                       os.path.join(B, "index.html"), hoje])
if "--publicar" in sys.argv:
    subprocess.check_call(["git", "-C", B, "add", "-A"])
    if subprocess.call(["git", "-C", B, "diff", "--cached", "--quiet"]) == 0:
        print("Nada mudou desde a última publicação.")
    else:
        subprocess.check_call(["git", "-C", B, "commit", "-m", f"Atualiza dados de {hoje}"])
        subprocess.check_call(["git", "-C", B, "push"])
        print("Publicado. O site atualiza em cerca de 1 minuto.")
