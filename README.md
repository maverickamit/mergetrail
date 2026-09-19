# MergeTrail

Open-source, agent-agnostic workspace for understanding and reviewing large pull requests.

Big changes are where review breaks down. Forty files in, you are still reconstructing what the
author was doing. MergeTrail reads the branch with `git`, renders it in a GitHub-style diff, and
puts a plain-language explanation next to every hunk so you can follow the shape of the change
instead of rebuilding it in your head.

Agent-agnostic means you choose the model. Bring an API key for Anthropic, OpenAI, or any
OpenAI-compatible endpoint, including a local one. Nothing is routed through a service we run: the
server is on your machine, and so is your code.

It is a tool for *understanding* a change quickly. It does not hunt for bugs, score your code, or
edit files.

## Status

Early. The project is being built in parts:

| Part | Scope | State |
| --- | --- | --- |
| 1 | Python project scaffold | done |
| 2 | Git layer: three-dot diffs, hunk parsing | done |
| 3 | FastAPI server and CLI | done |
| 4 | React review UI | planned |
| 5 | Per-hunk explanation panel | planned |
| 6 | Bring-your-own-key explanations | planned |

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- `git` on your `PATH`

## Development

```sh
uv sync
uv run mergetrail --base main --no-open
uv run pytest
uv run ruff check
```

With the server running:

```sh
curl -s http://127.0.0.1:8765/review
curl -s http://127.0.0.1:8765/files
curl -s http://127.0.0.1:8765/files/app.py
```

## Layout

```
src/mergetrail/   Python package: CLI, git layer, API, explanations
ui/               React review UI (added in part 4)
tests/            pytest suite
```

## License

[AGPL-3.0-or-later](LICENSE)
