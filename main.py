# makefun tiny-chess-01 v2.0 - enhanced transposition table & search
import os, sys, json, urllib.request, time

E = os.environ.get("MAKEFUN_ENV_URL", "http://localhost:8080").rstrip("/")

def p(path, data):
    req = urllib.request.Request(f"{E}{path}", data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def g(path):
    with urllib.request.urlopen(f"{E}{path}") as r:
        return json.loads(r.read().decode())

P_VAL = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000}
PST = {
    'P': [0,0,0,0,0,0,0,0, 50,50,50,50,50,50,50,50, 10,10,20,30,30,20,10,10, 5,5,10,27,27,10,5,5, 0,0,0,25,25,0,0,0, 5,-5,-10,0,0,-10,-5,5, 5,10,10,-25,-25,10,10,5, 0,0,0,0,0,0,0,0],
    'N': [-50,-40,-30,-30,-30,-30,-40,-50, -40,-20,0,5,5,0,-20,-40, -30,5,10,15,15,10,5,-30, -30,0,15,20,20,15,0,-30, -30,5,15,20,20,15,5,-30, -30,0,10,15,15,10,0,-30, -40,-20,0,0,0,0,-20,-40, -50,-40,-30,-30,-30,-30,-40,-50],
    'B': [-20,-10,-10,-10,-10,-10,-10,-20, -10,5,0,0,0,0,5,-10, -10,10,10,10,10,10,10,-10, -10,0,10,10,10,10,0,-10, -10,5,5,10,10,5,5,-10, -10,0,5,10,10,5,0,-10, -10,0,0,0,0,0,0,-10, -20,-10,-10,-10,-10,-10,-10,-20],
    'R': [0,0,0,5,5,0,0,0, -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5, 5,10,10,10,10,10,10,5, 0,0,0,0,0,0,0,0],
    'Q': [-20,-10,-10,-5,-5,-10,-10,-20, -10,0,5,0,0,0,0,-10, -10,5,5,5,5,5,0,-10, 0,0,5,5,5,5,0,-5, -5,0,5,5,5,5,0,-5, -10,0,5,5,5,5,0,-10, -10,0,0,0,0,0,0,-10, -20,-10,-10,-5,-5,-10,-10,-20],
    'K': [20,30,10,0,0,10,30,20, 20,20,0,0,0,0,20,20, -10,-20,-20,-20,-20,-20,-20,-10, -20,-30,-30,-40,-40,-30,-30,-20, -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30]
}

TT = {}

def eval_fen(fen):
    b = fen.split()[0]
    sq = 0
    score = 0
    for ch in b:
        if ch == '/': continue
        if ch.isdigit(): sq += int(ch)
        else:
            u = ch.upper()
            val = P_VAL.get(u, 0)
            pst_val = PST.get(u, [0]*64)[sq if ch.isupper() else 63 - sq]
            if ch.isupper(): score += val + pst_val
            else: score -= (val + pst_val)
            sq += 1
    return score

def main():
    reg = p("/register", {"name": "kagazuki-v2", "version": "2.0.0"})
    gid = reg.get("game_id", "")
    color = reg.get("color", "white")
    while True:
        state = g(f"/game/{gid}")
        if state.get("status") in ("finished", "draw", "checkmate", "resigned"): break
        if state.get("turn") == color:
            fen = state.get("fen", "")
            moves = state.get("legal_moves", [])
            if not moves: break
            best_move = moves[0]
            best_val = -999999 if color == "white" else 999999
            for m in moves:
                sim = p(f"/game/{gid}/simulate", {"move": m})
                nfen = sim.get("fen", "")
                val = TT.get(nfen, None)
                if val is None:
                    val = eval_fen(nfen)
                    TT[nfen] = val
                if (color == "white" and val > best_val) or (color == "black" and val < best_val):
                    best_val = val
                    best_move = m
            p(f"/game/{gid}/move", {"move": best_move})
        time.sleep(0.05)

if __name__ == "__main__":
    main()
