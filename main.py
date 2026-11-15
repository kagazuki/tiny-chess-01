import os, sys, json, urllib.request, time

E = os.environ.get("MAKEFUN_ENV_URL", "http://localhost:8080").rstrip("/")

def p(path, data):
    req = urllib.request.Request(f"{E}{path}", data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

V = {'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000}
C = [0, 10, 20, 25, 25, 20, 10, 0]

def parse(fen):
    b = {}
    for r, rank in enumerate(fen.split()[0].split('/')):
        c = 0
        for ch in rank:
            if ch.isdigit(): c += int(ch)
            else:
                b[chr(97 + c) + str(8 - r)] = ch
                c += 1
    return b

def pick(data):
    legal = data.get("legal_moves", [])
    if not legal: return None
    b = parse(data.get("fen", ""))
    best, best_s = legal[0], -1e9
    for m in legal:
        src, dst, promo = m[:2], m[2:4], m[4:]
        target = b.get(dst)
        piece = b.get(src, 'p').lower()
        s = 0
        if target:
            s += V.get(target.lower(), 0) * 10 - V.get(piece, 0)
        if promo:
            s += V.get(promo.lower(), 900)
        c, r = ord(dst[0]) - 97, int(dst[1]) - 1
        s += C[c] + C[r]
        if s > best_s:
            best_s, best = s, m
    return best

def main():
    while True:
        try:
            s = p("/game", {})
        except Exception:
            time.sleep(0.5)
            continue
        if s.get("status") == "done": break
        gid = s.get("game")
        while s.get("status") == "your_move":
            mv = pick(s)
            if not mv: break
            try:
                s = p("/move", {"game": gid, "move": mv})
            except Exception:
                break

if __name__ == "__main__":
    main()
