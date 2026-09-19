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
| 4 | React review UI | done |
| 5 | Per-hunk explanation panel | planned |
| 6 | Bring-your-own-key explanations | planned |

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- `git` on your `PATH`
- Node.js 20+ to build the review UI

## Development

```sh
uv sync
cd ui && npm install && npm run build && cd ..
uv run mergetrail --base main
uv run pytest
uv run ruff check
```

`mergetrail` serves the UI at `http://127.0.0.1:8765` and the JSON API under `/review` and `/files`.

To iterate on the UI without rebuilding:

```sh
uv run mergetrail --base main --no-open
cd ui && npm run dev
```

Vite proxies API calls to port 8765.

## Layout

```
src/mergetrail/   Python package: CLI, git layer, API, explanations
ui/               React review UI (added in part 4)
tests/            pytest suite
```

## License

[AGPL-3.0-or-later](LICENSE)
