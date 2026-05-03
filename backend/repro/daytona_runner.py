from __future__ import annotations

import base64
import csv
import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any


try:
    from dotenv import load_dotenv

    load_dotenv(".env")
    load_dotenv(".env.local", override=True)
    load_dotenv(".local.env", override=True)
except Exception:
    pass


DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-pro-preview")


class DaytonaGeminiReproRunner:
    """Run the reproducibility probe in Daytona with Gemini as the sandbox agent."""

    def __init__(self) -> None:
        self.gemini_model = DEFAULT_GEMINI_MODEL
        self.allow_local_fallback = os.getenv("REFEREEOS_ALLOW_LOCAL_REPRO_FALLBACK", "true").lower() == "true"

    def run(self, fixture_meta: dict[str, Any], paper: dict[str, Any]) -> dict[str, Any]:
        payload = self._build_payload(fixture_meta, paper)

        try:
            return self._run_in_daytona(payload)
        except Exception as exc:
            if not self.allow_local_fallback:
                return self._inconclusive_receipt(payload, f"Daytona run failed and fallback is disabled: {exc}")
            return self._run_local_fallback(payload, str(exc))

    def _build_payload(self, fixture_meta: dict[str, Any], paper: dict[str, Any]) -> dict[str, Any]:
        results_path = Path(fixture_meta["results_path"])
        script_path = Path(__file__).resolve().parents[1] / "fixtures" / "reproduce_metric.py"
        return {
            "fixture_id": fixture_meta.get("fixture_id", "uploaded"),
            "paper_title": paper.get("title"),
            "paper_summary": paper.get("abstract"),
            "reported_result": fixture_meta.get("reported_result"),
            "results_csv": results_path.read_text(encoding="utf-8") if results_path.exists() else "",
            "metric_script": script_path.read_text(encoding="utf-8"),
            "gemini_model": self.gemini_model,
            "gemini_api_key": _gemini_key_for_daytona(),
        }

    def _run_in_daytona(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not os.getenv("DAYTONA_API_KEY"):
            raise RuntimeError("DAYTONA_API_KEY is not set")

        try:
            from daytona import Daytona
        except Exception as exc:  # pragma: no cover - depends on sponsor SDK runtime
            raise RuntimeError("Daytona SDK is not installed") from exc

        daytona = Daytona()
        sandbox = daytona.create()
        try:
            code = _sandbox_code(payload)
            response = sandbox.process.code_run(code)
            exit_code = getattr(response, "exit_code", 0)
            result_text = getattr(response, "result", str(response))
            receipt = _parse_receipt(result_text)
            if not receipt:
                receipt = self._inconclusive_receipt(payload, "Daytona sandbox did not return receipt JSON.")
                receipt["stdout_stderr_summary"] = result_text[-1400:]
            receipt["exit_code"] = exit_code
            receipt["sandbox_provider"] = "Daytona"
            receipt["model"] = payload["gemini_model"]
            return receipt
        finally:
            try:
                daytona.delete(sandbox)
            except Exception:
                pass

    def _run_local_fallback(self, payload: dict[str, Any], reason: str) -> dict[str, Any]:
        temp_dir = Path("outputs") / "local_repro"
        temp_dir.mkdir(parents=True, exist_ok=True)
        results_path = temp_dir / f"{payload['fixture_id']}_results.csv"
        script_path = temp_dir / "reproduce_metric.py"
        results_path.write_text(payload["results_csv"], encoding="utf-8")
        script_path.write_text(payload["metric_script"], encoding="utf-8")

        completed = subprocess.run(
            [sys.executable, str(script_path), str(results_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        observed = _extract_metric(completed.stdout)
        reported = float(payload.get("reported_result") or 0)
        status = _status(reported, observed)
        followup = (
            "Ask authors to explain the metric mismatch before review."
            if status == "failed"
            else "Human reviewer should still inspect artifact scope and dataset representativeness."
        )

        return {
            "probe": "Gemini Pro 3.1 full reproducibility agent: select and run metric recalculation probe",
            "sandbox_provider": "local fallback (Daytona unavailable)",
            "model": payload["gemini_model"],
            "status": status,
            "commands_run": [f"{sys.executable} reproduce_metric.py {results_path.name}"],
            "reported_result": f"{reported:.2f}",
            "observed_result": f"{observed:.2f}" if observed is not None else "unavailable",
            "artifact_paths": [str(results_path), str(script_path)],
            "stdout_stderr_summary": (completed.stdout + completed.stderr).strip(),
            "human_followup": followup,
            "gemini_interpretation": (
                "Development fallback used because Daytona/Gemini was not reachable locally. "
                f"Fallback reason: {reason}"
            ),
            "exit_code": completed.returncode,
        }

    def _inconclusive_receipt(self, payload: dict[str, Any], reason: str) -> dict[str, Any]:
        return {
            "probe": "Gemini Pro 3.1 full reproducibility agent: select and run metric recalculation probe",
            "sandbox_provider": "Daytona",
            "model": payload["gemini_model"],
            "status": "inconclusive",
            "commands_run": [],
            "reported_result": str(payload.get("reported_result")),
            "observed_result": "unavailable",
            "artifact_paths": [],
            "stdout_stderr_summary": reason,
            "human_followup": "Retry the Daytona sandbox run and ask authors for executable artifacts if it fails again.",
            "gemini_interpretation": reason,
            "exit_code": 1,
        }


def _sandbox_code(payload: dict[str, Any]) -> str:
    encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
    return textwrap.dedent(
        f"""
        import base64
        import json
        import os
        import re
        import subprocess
        import sys
        import urllib.request
        from pathlib import Path

        payload = json.loads(base64.b64decode("{encoded}").decode("utf-8"))
        Path("results.csv").write_text(payload["results_csv"], encoding="utf-8")
        Path("reproduce_metric.py").write_text(payload["metric_script"], encoding="utf-8")

        completed = subprocess.run(
            [sys.executable, "reproduce_metric.py", "results.csv"],
            capture_output=True,
            text=True,
            check=False,
        )

        metric_match = re.search(r"macro_f1=([0-9.]+)", completed.stdout)
        observed = float(metric_match.group(1)) if metric_match else None
        reported = float(payload.get("reported_result") or 0)
        if observed is None:
            status = "inconclusive"
        elif abs(observed - reported) <= 0.01:
            status = "passed"
        else:
            status = "failed"

        prompt = f'''
        You are Gemini Pro 3.1 running inside a Daytona sandbox as the full reproducibility agent for RefereeOS.
        Paper: {{payload["paper_title"]}}
        Reported macro F1: {{reported:.2f}}
        Observed macro F1 from artifact rerun: {{observed if observed is not None else "unavailable"}}
        Process exit code: {{completed.returncode}}
        Stdout: {{completed.stdout}}
        Stderr: {{completed.stderr}}

        Return a terse JSON object with keys interpretation and human_followup.
        Do not recommend accept or reject publication.
        '''

        def ask_gemini() -> dict:
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or payload.get("gemini_api_key")
            model = os.getenv("GEMINI_MODEL", payload.get("gemini_model", "gemini-3.1-pro-preview"))
            if not api_key:
                return {{
                    "interpretation": "Gemini sponsor credentials were not visible in the sandbox, so the sandbox used deterministic interpretation after running the artifact.",
                    "human_followup": "Confirm sponsor Gemini environment variables are mounted for live judging."
                }}

            body = {{
                "contents": [{{"parts": [{{"text": prompt}}]}}],
                "generationConfig": {{"responseMimeType": "application/json"}}
            }}
            request = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{{model}}:generateContent?key={{api_key}}",
                data=json.dumps(body).encode("utf-8"),
                headers={{"Content-Type": "application/json"}},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=35) as response:
                    response_json = json.loads(response.read().decode("utf-8"))
                text = response_json["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
            except Exception as exc:
                return {{
                    "interpretation": f"Gemini API call failed inside Daytona after artifact execution: {{exc}}",
                    "human_followup": "Inspect Gemini sponsor configuration and rerun the Daytona reproducibility agent."
                }}

        gemini = ask_gemini()
        if status == "failed":
            default_followup = "Ask authors to explain the metric mismatch before review."
        elif status == "passed":
            default_followup = "Human reviewer should inspect artifact scope, but the metric receipt matches."
        else:
            default_followup = "Ask authors for a runnable artifact or clearer metric definition."

        receipt = {{
            "probe": "Gemini Pro 3.1 full reproducibility agent: select and run metric recalculation probe",
            "sandbox_provider": "Daytona",
            "model": payload.get("gemini_model", "gemini-3.1-pro-preview"),
            "status": status,
            "commands_run": [f"{{sys.executable}} reproduce_metric.py results.csv"],
            "reported_result": f"{{reported:.2f}}",
            "observed_result": f"{{observed:.2f}}" if observed is not None else "unavailable",
            "artifact_paths": ["results.csv", "reproduce_metric.py"],
            "stdout_stderr_summary": (completed.stdout + completed.stderr).strip(),
            "human_followup": gemini.get("human_followup") or default_followup,
            "gemini_interpretation": gemini.get("interpretation") or "Gemini completed the reproducibility interpretation.",
            "exit_code": completed.returncode,
        }}
        print(json.dumps(receipt))
        """
    )


def _gemini_key_for_daytona() -> str:
    pass_key = os.getenv("REFEREEOS_PASS_GEMINI_KEY_TO_DAYTONA", "false").lower() == "true"
    if not pass_key:
        return ""
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""


def _parse_receipt(result_text: str) -> dict[str, Any] | None:
    for line in reversed(result_text.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    return None


def _extract_metric(stdout: str) -> float | None:
    match = re.search(r"macro_f1=([0-9.]+)", stdout)
    return float(match.group(1)) if match else None


def _status(reported: float, observed: float | None) -> str:
    if observed is None:
        return "inconclusive"
    return "passed" if abs(observed - reported) <= 0.01 else "failed"
