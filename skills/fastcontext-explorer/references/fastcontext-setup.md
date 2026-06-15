# FastContext Setup Reference

Use this reference only when the user asks to install, configure, or debug the FastContext MCP integration.

## Bundled FastContext Runtime

Installing `fastcontext-agent-tools` also installs Microsoft FastContext from a
pinned official source revision:

```bash
python -m pip install -e .
```

The MCP server runs `python -m fastcontext.cli` with the same Python interpreter.
There is no separate CLI installation or PATH requirement. The package does not
download model weights or start an inference server.

## Endpoint Environment

FastContext expects an OpenAI-compatible endpoint:

```bash
export BASE_URL="https://your-endpoint.example/v1"
export MODEL="microsoft/FastContext-1.0-4B-SFT"
export API_KEY="your-api-key"
```

`API_KEY` can be omitted only when the endpoint does not require authentication.

## Repository Allowlist

Set `FASTCONTEXT_ALLOWED_ROOTS` to restrict what the MCP server may explore:

```bash
export FASTCONTEXT_ALLOWED_ROOTS="/Users/me/projects:/Users/me/work"
```

If unset, the MCP server allows only repositories under the directory where the server process starts.
