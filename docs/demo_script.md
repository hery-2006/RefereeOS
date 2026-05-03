# RefereeOS Demo Script

## 90 Seconds

Scientific review is bottlenecked, and AI-written manuscripts can make weak work look polished.

RefereeOS does not replace peer review. It prepares peer review.

Start with the clean fixture. The AG2 workflow extracts claims, surfaces evidence, checks methods, runs an integrity scan, and sends the reproducibility probe into Daytona.

The Daytona sandbox runs the artifact and OpenAI GPT-5.5 interprets the reproducibility receipt, producing the reported result, observed result, status, and human follow-up.

Switch to the suspicious fixture. The evidence board now flags an embedded prompt-injection instruction and a metric mismatch.

Alternate path: upload the manuscript, CSV artifact, metric script, and reported value directly. This produces the same Daytona receipt without relying on the fixture selector.

Close: RefereeOS routes scarce human expertise to the papers and claims that need attention most.

## Five Minutes

- 45s: Problem and ethical boundary.
- 45s: Architecture: AG2 agents, JSON evidence board, Daytona sandbox, OpenAI GPT-5.5 repro agent.
- 2m: Live clean fixture and suspicious fixture.
- 45s: Why AG2 and Daytona matter.
- 45s: Limitations and next steps.
