# FC-Play Smoke Tests

These tests validate FC-Play works end-to-end in a live environment.

## Running

```bash
uv run pytest smoke/ -v --tb=short
```

## Prerequisites

- FC-Play server running locally
- At least one API key configured in `~/.fc-play/.env`
