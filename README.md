# tiny-chess-01: 4KB Chess Engine

Autonomous chess engine submission for make.fun tiny-chess-01 competition.

## Architecture
- Single file self-contained in `main.py` (< 2 KB).
- Evaluates material values and center control metrics.
- Uses native HTTP/JSON requests with the evaluation harness environment (`MAKEFUN_ENV_URL`).
- Zero external dependencies.
