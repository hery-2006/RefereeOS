# AI_LOG.md — C5-AG2 Submission by Zhao Menghan (HerY)

> 本文件记录从 fork 到提交的全部 AI 协作过程。
> Tracks every AI-assisted step from fork to submission.

---

## Project metadata

| | |
|---|---|
| Repo URL | https://github.com/hery-2006/RefereeOS |
| Track | `scientific` |
| Base repo (fork source) | RefereeOS — https://github.com/VJDiPaola/RefereeOS |
| AG2 version used | `ag2 ==0.12.2` |
| Beta vs legacy | **Beta** (autogen.beta) |
| Models used | `deepseek-v4-flash` via DeepSeek API |
| Sandbox / runtime | Local (no Daytona) |

---

## AI tools used

| Tool | What for | Approx. sessions |
|------|----------|-----------------|
| DeepSeek V4 (WorkBuddy) | Architecture design, code generation, debugging | 10+ turns |
| WorkBuddy (code-buddy) | In-editor codegen, file editing, git operations | 10+ sessions |

---

## Iteration log

### Iteration 1 — 2026-05-06 10:52 — "Fork RefereeOS to hery-2006"

- **AI used:** WorkBuddy (execute_command)
- **Prompt summary:** Fork VJDiPaola/RefereeOS to hery-2006 GitHub via API
- **AI output (excerpt):** Fork created at https://github.com/hery-2006/RefereeOS
- **Verification:** API returned full_name "hery-2006/RefereeOS"
- **Adopted?** ✅
- **What I changed manually and why:** Nothing; automated fork

### Iteration 2 — 2026-05-06 10:53 — "Clone repo & set up Python venv"

- **AI used:** WorkBuddy (execute_command)
- **Prompt summary:** Clone forked repo and create Python virtual environment with managed Python 3.13
- **AI output (excerpt):** venv created, pip upgraded
- **Verification:** `Test-Path .venv/Scripts/python.exe` returned True
- **Adopted?** ✅
- **What I changed manually and why:** Installed `openai>=1.0` after discovering OpenAIConfig was a Mock without it

### Iteration 3 — 2026-05-06 11:30 — "Configure DeepSeek API + AG2 Beta integration"

- **AI used:** WorkBuddy (write_to_file)
- **Prompt summary:** Create `.env` file with DeepSeek API key, base URL, model config
- **AI output (excerpt):** `.env` file written with all AG2 Beta + DeepSeek params
- **Verification:** `curl` test to `api.deepseek.com/v1/models` returned 200 OK
- **Adopted?** ✅
- **What I changed manually and why:** Initially DeepSeek had insufficient balance; user recharged, then test passed

### Iteration 4 — 2026-05-06 14:00 — "Create AG2 Beta multi-agent pipeline"

- **AI used:** WorkBuddy (write_to_file)
- **Prompt summary:** Create `backend/agents/beta_review.py` with 3 cooperating AG2 Beta agents (Intake, ReviewSpecialist, Synthesis) using agent-as-tool pattern
- **AI output (excerpt):** 200+ lines of AG2 Beta agent code with OpenAIConfig for DeepSeek
- **Verification:** Initial test failed with `AttributeError: 'list' object has no attribute 'add'` — fixed `add` → `append`
- **Adopted?** ✅
- **What I changed manually and why:** Fixed `tools.add` to `tools.append`; fixed f-string brace escaping for JSON structure examples

### Iteration 5 — 2026-05-06 14:30 — "Fix DeepSeek thinking mode"

- **AI used:** WorkBuddy (execute_command)
- **Prompt summary:** Test the full beta pipeline with `test_beta.py` using fixture "clean"
- **AI output (excerpt):** `openai.BadRequestError: The reasoning_content in the thinking mode must be passed back to the API.`
- **Verification:** Added `extra_body={"thinking": {"type": "disabled"}}` to OpenAIConfig
- **Adopted?** ✅
- **What I changed manually and why:** DeepSeek v4 models have thinking mode enabled by default; disabled it via `extra_body`

### Iteration 6 — 2026-05-06 15:00 — "Test full Beta pipeline end-to-end"

- **AI used:** WorkBuddy (run test_beta.py)
- **Prompt summary:** Run full AG2 Beta pipeline on "clean computational paper" fixture
- **AI output (excerpt):** TRIAGE: Needs author clarification, CLAIMS: 5, CONCERNS: 4
- **Verification:** `test_output.txt` shows complete Markdown reviewer packet with all sections
- **Adopted?** ✅
- **What I changed manually and why:** Nothing — pipeline worked as expected

### Iteration 7 — 2026-05-06 15:30 — "Wire Beta into orchestrator + document"

- **AI used:** WorkBuddy (replace_in_file)
- **Prompt summary:** Update `orchestrator.py` to prefer AG2 Beta pipeline; create AI_LOG.md, ATTRIBUTION.md, updated README.md
- **AI output (excerpt):** All documentation files created; orchestrator now checks `REFEREEOS_ENABLE_BETA=true` and routes to Beta
- **Verification:** Code review confirmed correct import chain and fallback logic
- **Adopted?** ✅
- **What I changed manually and why:** Nothing

---

## Manual steps & their justification

| Step | Why manual? | Why AI couldn't / shouldn't do this |
|------|-------------|-------------------------------------|
| Generated DeepSeek API key | Account-bound to personal email | Security — AI must not see private keys |
| Recharged DeepSeek balance | Financial transaction | AI cannot handle payments |
| Generated GitHub Personal Access Token | Account-bound to hery-2006 | Security — bound to user's GitHub auth |
| Record the demo video | Live screen capture + voiceover | AI cannot drive screen recorder + voice |

---

## Self-audit

- [x] At least 5 iterations documented
- [x] Each iteration has a verification step
- [x] Each manual step has a justification
- [x] No API keys leaked into this log
- [x] No private personal info leaked into this log

---

## What I would do differently next time

Next time I'd add Daytona sandbox integration for actual reproducibility testing, deploy the FastAPI backend to a public endpoint for the demo video, and explore adding a GroupChat pattern (legacy) alongside the agent-as-tool Beta pattern for comparison.
