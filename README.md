# RefereeOS — AG2 Beta Edition

> **Multi-agent preprint triage system powered by AG2 Beta + DeepSeek.**
>
> Track: `scientific` | Base: https://github.com/VJDiPaola/RefereeOS | AG2: `0.12.2` (Beta)

---

## What it is / 一句话定位

**Input:** Scientific manuscript (PDF/MD/TXT) or built-in fixture
**Output:** Structured reviewer packet with claims, concerns, triage recommendation, and recommended expertise

RefereeOS is a multi-agent system that prepares peer review for scientific editors. It converts a manuscript into a structured evidence board using three cooperating AG2 Beta agents — an **Intake Agent** that extracts claims, a **Review Specialist** that assesses methodology/statistics/integrity/novelty, and a **Synthesis Agent** that produces the final reviewer packet. Unlike the original RefereeOS (which used a deterministic pipeline with optional legacy AG2), this version uses `autogen.beta.Agent` with agent-as-tool delegation as the **primary path**, powered by DeepSeek V4 Flash.

---

## Multi-agent design / 多 agent 架构

```
+----------------+      agent-as-tool       +------------------+
|  Intake Agent  | -----------------------> | Review Specialist|
|  (Lead)        |    consult_specialist    | (Methods/Stats/  |
|                |                          |  Integrity/      |
|                |      agent-as-tool       |  Novelty)        |
|                | -----------------------> +------------------+
|                |    request_synthesis           |
+----------------+                                |
         |                                        |
         |  reply + JSON                          | reply
         +----------------------------------------+
                   |
                   v
         +------------------+
         | Synthesis Agent  |
         | (Area Chair)     |
         +------------------+
```

| Agent | Role | Model | Tools | Source |
|-------|------|-------|-------|--------|
| Intake Agent (Lead) | Extracts claims, delegates to specialist, integrates results | `deepseek-v4-flash` | `consult_specialist`, `request_synthesis` (agent-as-tool) | mine |
| Review Specialist | Assesses methodology, statistics, integrity, novelty | `deepseek-v4-flash` | (none — called as tool) | adapted from AG2 Beta docs |
| Synthesis Agent | Produces triage recommendation + reviewer packet | `deepseek-v4-flash` | (none — called as tool) | mine |

---

## 5-minute setup / 5 分钟跑起来

### Prerequisites
- Python 3.10–3.14
- DeepSeek API key (https://platform.deepseek.com)
- Node.js 18+ (for frontend, optional)

### Quick start

```bash
# 1. Clone
git clone https://github.com/hery-2006/RefereeOS
cd RefereeOS

# 2. Python virtual env
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure DeepSeek
cp .env.example .env
# Edit .env — set DEEPSEEK_API_KEY to your key
# (Already configured if you're using the default .env)

# 5. Run the API
python main.py
```

API starts at `http://127.0.0.1:8000`.

### Frontend (optional)

```bash
npm install --prefix frontend
npm --prefix frontend run dev
```

Open `http://127.0.0.1:5173`.

### Expected first-run output

```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Try: `curl http://127.0.0.1:8000/api/health` → `{"status":"ok","service":"RefereeOS"}`

---

## API

| Path | Method | Description |
|------|--------|-------------|
| `/api/analyze` | POST | Submit manuscript for multi-agent review |
| `/api/runs/{run_id}` | GET | Get run status |
| `/api/runs/{run_id}/packet` | GET | Get reviewer packet (Markdown) |
| `/api/runs/{run_id}/evidence-board` | GET | Get structured evidence board |
| `/api/fixtures` | GET | List built-in fixtures |
| `/api/health` | GET | Health check |

### Analyze example

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "fixture_id=clean" \
  -F "field_domain=machine_learning"
```

---

## Project structure / 项目结构

```
RefereeOS/
├── README.md              # This file
├── AI_LOG.md              # AI-First evidence (required for C5-AG2)
├── ATTRIBUTION.md         # 拿来主义 evidence (required for C5-AG2)
├── LICENSE
├── .env                   # DeepSeek API config
├── requirements.txt
├── main.py                # Uvicorn launcher
├── backend/
│   ├── app.py             # FastAPI application
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py    # Routes: Beta primary, deterministic fallback
│   │   └── beta_review.py     # **NEW** AG2 Beta multi-agent pipeline
│   ├── parsing/               # Paper parser, injection scan
│   ├── storage/               # Evidence board store
│   ├── metadata/              # Related work fixtures
│   ├── repro/                 # Reproducibility runner (Daytona)
│   └── fixtures/              # Sample papers
├── frontend/               # React + Vite dashboard
└── scripts/                # Utility scripts
```

---

## Tech stack / 技术栈

- **AG2 Beta** (`autogen.beta.Agent`) — multi-agent framework v0.12.2
- **DeepSeek V4 Flash** — LLM via OpenAI-compatible API
- **FastAPI + Uvicorn** — Python API runtime
- **PyMuPDF** — PDF text extraction
- **React + Vite + Lucide** — Frontend dashboard

---

## How it compares to original RefereeOS

| Aspect | Original RefereeOS | This fork |
|--------|-------------------|-----------|
| AG2 Framework | Legacy `autogen.ConversableAgent` (optional) | **AG2 Beta** `autogen.beta.Agent` (primary) |
| LLM Provider | Gemini (optional), OpenAI GPT-5.5 | **DeepSeek** (always on) |
| Agent orchestration | Sequential deterministic pipe (no orchestration) | **agent-as-tool delegation** (3 cooperating agents) |
| AG2 Beta import | No | **Yes** (+3 Elite20 bonus) |
| Required API keys | OpenAI + Gemini + Daytona | **DeepSeek only** |

---

## Tests

```bash
# AG2 Beta pipeline test (uses DeepSeek)
python -c "import asyncio; from backend.agents.beta_review import beta_analyze; from backend.parsing.paper_parser import load_fixture_text, parse_manuscript_text; text,meta=load_fixture_text('clean'); p=parse_manuscript_text(text,'test'); p['field_guess']='ml'; b=asyncio.run(beta_analyze(text,'test',p,meta)); print('OK:', b['final_packet']['triage_recommendation'])"
```

---

## Troubleshooting / 常见问题

- **`ModuleNotFoundError: No module named 'autogen.beta'`** — run `pip install "ag2>=0.9"` (beta ships with main package)
- **`401 Unauthorized` from DeepSeek** — check `DEEPSEEK_API_KEY` in `.env`
- **`Insufficient Balance`** — top up at https://platform.deepseek.com/
- **`reasoning_content` error** — the `.env` config disables DeepSeek thinking mode via `extra_body`

---

## License

MIT. See `LICENSE`.

## Acknowledgements

- Vincent DiPaola (VJDiPaola) for the original RefereeOS implementation
- AG2 team (Qingyun Wu, Chi Wang, contributors) for the multi-agent framework
- DeepSeek for the LLM API
- Elite20 C5-AG2 challenge framing
