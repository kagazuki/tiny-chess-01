# makefun tiny-chess-01 v3.1 - positional chess engine
import os, json, urllib.request, zlib, base64

E = os.environ.get('MAKEFUN_ENV_URL', 'http://localhost:8080').rstrip('/')

def p(path, data):
    req = urllib.request.Request(f'{E}{path}', data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

V = {1: 100, 2: 320, 3: 330, 4: 500, 5: 900, 6: 20000}
_b = base64.b64decode('eJyFTyESBCEM+yEajVlTXYOJqanB1OzsDI+4F14Kuzdnbi6igZQ0FNh43XCPOcPdzK+Lla3zZLGugHbKfhxs3zaU2ohaqoCPpTbzMdxaw4gYaM2S8546Gt8RUh+f6ILommiqvqCKJKhmolFHMu87Vh9fmtLat97/se35n/9zTu+ZjyVlHgHNsWT6Nuvm7/zli+mAz4hIOUJlQYXLcUVhLSVPP/gNg8S4lA==')
_r = [b - 128 for b in zlib.decompress(_b)]
PST = {k: _r[(k - 1) * 64 : k * 64] for k in range(1, 7)}

def fen_to_board(fen):
    b, sq, m = [0] * 64, 0, {'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6, 'p': -1, 'n': -2, 'b': -3, 'r': -4, 'q': -5, 'k': -6}
    for ch in fen.split()[0]:
        if ch == '/': continue
        if ch.isdigit(): sq += int(ch)
        else:
            b[sq] = m.get(ch, 0)
            sq += 1
    return b

def u2s(m):
    return (8 - int(m[1])) * 8 + (ord(m[0]) - 97), (8 - int(m[3])) * 8 + (ord(m[2]) - 97)

def eval_b(b):
    tot = 0
    for sq in range(64):
        p = b[sq]
        if p:
            k = abs(p)
            v = V[k] + PST[k][sq if p > 0 else 63 - sq]
            tot += v if p > 0 else -v
    return tot

def is_atk(b, sq, w):
    s = 8 if w else -8
    for d in (-1, 1):
        if 0 <= (sq % 8) + d < 8 and 0 <= sq + s + d < 64:
            if b[sq + s + d] == (1 if w else -1): return True
    for ro, co in ((r, c) for r in (-2,-1,1,2) for c in (-2,-1,1,2) if abs(r) != abs(c)):
        r, c = sq // 8 + ro, sq % 8 + co
        if 0 <= r < 8 and 0 <= c < 8 and b[r * 8 + c] == (2 if w else -2): return True
    for dirs, pcs in [(((-1,-1),(-1,1),(1,-1),(1,1)), (3, 5)), (((-1,0),(1,0),(0,-1),(0,1)), (4, 5))]:
        for dr, dc in dirs:
            r, c = sq // 8 + dr, sq % 8 + dc
            while 0 <= r < 8 and 0 <= c < 8:
                p = b[r * 8 + c]
                if p:
                    if (p in pcs if w else -p in pcs): return True
                    break
                r, c = r + dr, c + dc
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr or dc:
                r, c = sq // 8 + dr, sq % 8 + dc
                if 0 <= r < 8 and 0 <= c < 8 and b[r * 8 + c] == (6 if w else -6): return True
    return False

def choose_move(fen, legal, colour):
    w = colour == 'white'
    b = fen_to_board(fen)
    best_m, best_s = legal[0], -999999 if w else 999999
    for m in legal:
        s1, s2 = u2s(m)
        p, tgt = b[s1], b[s2]
        nb = list(b)
        nb[s2], nb[s1] = (5 if w else -5) if len(m) == 5 else p, 0
        sc = eval_b(nb)
        if tgt:
            bns = V[abs(tgt)] * 10 - V[abs(p)]
            sc += bns if w else -bns
        if is_atk(nb, s2, not w):
            if not is_atk(nb, s2, w):
                sc += (-V[abs(p)] * 4) if w else (V[abs(p)] * 4)
            elif abs(p) > abs(tgt) and tgt:
                sc += -(V[abs(p)] - V[abs(tgt)]) * 2 if w else (V[abs(p)] - V[abs(tgt)]) * 2
        if (w and sc > best_s) or (not w and sc < best_s):
            best_s, best_m = sc, m
    return best_m

def main():
    while True:
        try:
            st = p('/game', {})
        except Exception:
            break
        if st.get('status') == 'done': break
        gid = st.get('game')
        while st.get('status') == 'your_move':
            leg = st.get('legal_moves', [])
            if not leg: break
            mv = choose_move(st.get('fen', ''), leg, st.get('colour', 'white'))
            st = p('/move', {'game': gid, 'move': mv})
            if st.get('status') in ('over', 'done'): break
        if st.get('next_game') is None or st.get('status') == 'done': break

if __name__ == '__main__':
    main()
