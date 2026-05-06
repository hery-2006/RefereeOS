# ATTRIBUTION.md — C5-AG2 Submission by Zhao Menghan (HerY)

> Elite20 拿来主义 (fork-and-improve) principle: every reused fragment is cited.

---

## 1. Fork source / Fork 源

| | |
|---|---|
| Base project | RefereeOS |
| Base repo URL | https://github.com/VJDiPaola/RefereeOS |
| Base captain | Vincent DiPaola |
| My fork URL | https://github.com/hery-2006/RefereeOS |
| Fork commit SHA at fork time | (latest commit of base repo at time of fork) |
| Track inheritance | base `scientific` → mine: `scientific` |

---

## 2. AG2 documentation references / AG2 文档引用

| File in my repo | Lines | Source doc | Verbatim / Adapted |
|-----------------|-------|------------|--------------------|
| `backend/agents/beta_review.py` | 1-60 | `references/ag2_docs/20_beta_example_hello_agent.mdx` (from C5 starter) | adapted: changed model, added 2 more agents, tool wiring |
| `backend/agents/beta_review.py` | 62-150 | `references/ag2_docs/13_beta_task_delegation.mdx` (from C5 starter) | adapted: agent-as-tool delegation pattern |
| `backend/agents/beta_review.py` | 150-220 | `references/ag2_docs/21_beta_example_research_squad.mdx` (from C5 starter) | adapted: multi-agent coordination pattern |
| `backend/agents/orchestrator.py` | beta_runtime detection | `references/ag2_docs/10_beta_motivation.mdx` (from C5 starter) | adapted: AG2 Beta detection logic |

---

## 3. Code reused from sample repos / 借鉴自样本 repo

| Source repo | Source file | Used in my repo | Notes |
|-------------|-------------|-----------------|-------|
| VJDiPaola/RefereeOS | `backend/agents/orchestrator.py` | `backend/agents/orchestrator.py` | Preserved deterministic fallback; added Beta routing |
| VJDiPaola/RefereeOS | `backend/app.py` | `backend/app.py` | FastAPI endpoints kept as-is |
| VJDiPaola/RefereeOS | `backend/parsing/paper_parser.py` | `backend/parsing/paper_parser.py` | Preserved fixture loading and parsing |
| VJDiPaola/RefereeOS | `backend/storage/evidence_board.py` | `backend/storage/evidence_board.py` | Preserved evidence board schema |
| VJDiPaola/RefereeOS | `frontend/` | `frontend/` | Frontend dashboard kept as-is |
| VJDiPaola/RefereeOS | `requirements.txt` | `requirements.txt` | Removed Daytona/OpenAI deps; kept core stack |

---

## 4. Prompts and prompt fragments / 提示词与提示词片段

| Used in | Source | Verbatim / Adapted |
|---------|--------|--------------------|
| `backend/agents/beta_review.py:create_intake_agent` | Original (mine) | — |
| `backend/agents/beta_review.py:create_review_specialist` | Adapted from AG2 Beta doc examples | adapted |
| `backend/agents/beta_review.py:create_synthesis_agent` | Original (mine) | — |

---

## 5. What I added / created / 我新增的部分

- **`backend/agents/beta_review.py`**: Entirely new file. Complete AG2 Beta multi-agent pipeline with 3 cooperating agents (Intake, ReviewSpecialist, Synthesis). Uses `autogen.beta.Agent` with agent-as-tool delegation pattern and DeepSeek via `OpenAIConfig`. Includes evidence-board builder, Markdown packet generator, and JSON output parser.

- **`.env`**: New configuration file with DeepSeek API key, base URL, model settings, and AG2 Beta flags.

- **Modified `backend/agents/orchestrator.py`**: Added `detect_beta_runtime()` function and Beta routing logic. Primary path now goes through AG2 Beta; deterministic fallback preserved.

- **`AI_LOG.md`**: Full AI-First evidence log with 7 verifiable iterations documenting every AI-assisted step.

- **`ATTRIBUTION.md`**: Complete 拿来主义 record with fork source, document references, and code reuse tracking.

- **`README.md` update**: Updated to reflect AG2 Beta + DeepSeek as primary pipeline, new setup instructions, and architecture diagram.

---

## 6. License compatibility check

| Source | Source license | Compatible with my license? |
|--------|---------------|----------------------------|
| VJDiPaola/RefereeOS (base repo) | MIT | ✅ My repo: MIT |
| AG2 framework (ag2ai/ag2) | Apache 2.0 | ✅ |
| build-with-ag2 examples | Apache 2.0 | ✅ |

---

## 7. Self-audit

- [x] Every code block >= 5 lines copied from elsewhere is cited above
- [x] My fork source is identified (RefereeOS by Vincent DiPaola)
- [x] License compatibility checked
- [x] Section 5 ("What I added") is non-trivial (>= 3 substantive items)
