from __future__ import annotations

import os


def main() -> int:
    """Small Daytona smoke test without hardcoded credentials."""
    if not os.getenv("DAYTONA_API_KEY"):
        print("Set DAYTONA_API_KEY before running this Daytona smoke test.")
        return 1

    from daytona import Daytona

    daytona = Daytona()
    sandbox = daytona.create()
    try:
        response = sandbox.process.code_run('print("Hello World from Daytona!")')
        if response.exit_code != 0:
            print(f"Error: {response.exit_code} {response.result}")
            return response.exit_code
        print(response.result)
        return 0
    finally:
        try:
            daytona.delete(sandbox)
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
