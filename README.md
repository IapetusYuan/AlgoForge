# AlgoForge 🔥

**English** | [繁體中文](./README.zh-TW.md)

> **Forge your algorithmic intuition, one problem a day.**
> An AI solving *coach* for LeetCode — it doesn't just hand you the answer, it teaches you **how to think**: how to approach a problem, which pattern to reach for, and how to *derive* time & space complexity instead of memorizing Big-O.

AlgoForge fetches the LeetCode daily problem (or any problem you pick), and a Claude Code agent produces a structured, teaching-first analysis: the thinking framework, the core idea, Java/C++ solutions, step-by-step complexity derivation, and the reusable pattern — all saved as Markdown and browsable in a dashboard.

![AlgoForge dashboard — problem list with pattern tags on the left, and a rendered teaching analysis with time/space complexity pills on the right](./docs/dashboard.png)

> 📄 See real output in [`examples/`](./examples) — e.g. [Two Sum](./examples/1-two-sum.md), or [GCD of Odd and Even Sums](./examples/3658-gcd-of-odd-and-even-sums.md) for the community solution comparison section in action.

## Why it's different

- **Teaches the approach, not just the answer** — reconstructs how a strong solver's mind moves: signals → ruled-out paths → why it converges on this solution.
- **Derives complexity, never just states it** — explains *which loop runs how many times*, not a bare `O(n)`.
- **Honest brute force first** — shows the naive solution, points out where it wastes work, *then* motivates the optimization.
- **Generalizes to patterns** — every problem is filed under a reusable pattern so you recognize it next time.

## The coach agent ⭐

The heart of AlgoForge is [`.claude/agents/algoforge-coach.md`](./.claude/agents/algoforge-coach.md) — a Claude Code subagent encoding the teaching rules above. Drop it into any Claude Code project and ask it to analyze a problem.

## Architecture

```
LeetCode GraphQL ──► Backend (Python / FastAPI) ──► Markdown notes + index
                          fetch / proxy CORS          │
                                                       ├──► Web dashboard
   you ◄── discuss ──► Claude coach agent ─────────────┘
```

- **Backend** — FastAPI proxies LeetCode GraphQL (avoids CORS), saves problems as Markdown stubs
- **Coach agent** — Claude Code fills in the 9-section teaching analysis (including an optional community solution comparison)
- **Dashboard** — problem list, pattern filter, note rendering, complexity pills, stats & spaced-review queue
- **Knowledge export** — turns solved problems into an Obsidian wiki (problem ↔ pattern backlinks)

## Project structure

```
AlgoForge/
├── backend/app/        # FastAPI backend
│   ├── leetcode.py     #   GraphQL client (daily / number / slug)
│   ├── htmlmd.py       #   HTML → Markdown
│   ├── storage.py      #   stub storage + index sync + stats/review
│   ├── obsidian.py     #   export to an Obsidian knowledge base
│   ├── solutions.py    #   fetch top-voted community solutions (coach reference material)
│   ├── main.py         #   REST API + serves the frontend
│   └── cli.py          #   command-line fetch / export / community solutions
├── frontend/           # web dashboard (no build step)
├── templates/          # the 9-section note template
├── examples/           # a curated sample analysis (Two Sum)
├── .claude/agents/     # the algoforge-coach agent ⭐
└── data/problems/      # your own analyses (gitignored)
```

## Quick start

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python -m app.cli daily            # fetch today's daily problem
uvicorn app.main:app --port 8642   # serve API + dashboard
python -m app.cli export           # export solved problems to an Obsidian wiki
```

Open <http://127.0.0.1:8642/> for the dashboard. Use the `algoforge-coach` agent in Claude Code to fill in each analysis. Exported wiki path defaults to `D:\Iapetus\AlgoForge`, override with `ALGOFORGE_VAULT`.

## CLI

| Command | What it does |
|---------|--------------|
| `python -m app.cli daily` | Fetch the LeetCode daily problem |
| `python -m app.cli 1` | Fetch by problem number |
| `python -m app.cli two-sum` | Fetch by title slug |
| `python -m app.cli export` | Export solved problems to Obsidian |
| `python -m app.cli solutions 1` | Fetch top-voted community solutions for a problem (coach reference material; `--top N` to adjust count) |

## API

`GET /api/daily` · `GET /api/problem/{id|slug}` · `GET /api/problems` · `GET /api/problem/{id|slug}/solutions` · `GET /api/problems/{id}/note` · `GET /api/stats` · `GET /api/review` · `POST /api/export`

> ⚠️ Both the problem-fetching and community-solutions endpoints are **unofficial** (undocumented LeetCode GraphQL) — fine for personal, low-frequency use, but they may change or get rate-limited at any time. A failed fetch degrades gracefully (the section is just skipped) rather than breaking the analysis.

## Tests

```bash
cd backend && pip install pytest && pytest
```

## Using it yourself (private data)

Your own solving notes live in `data/problems/` and are **gitignored** — the public repo ships only the engine plus curated `examples/`. To version your personal solutions, keep a private mirror that tracks this repo as `upstream`, and un-ignore `data/problems/` there.

## License

MIT — see [LICENSE](./LICENSE).
