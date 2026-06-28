# FastContext MCP 使用說明（繁體中文）

這個專案把 Microsoft FastContext 包成 MCP stdio server，讓 LLM coding agent 可以用 read-only 的方式探索 repo，取得相關檔案與行號，再由主 agent 自己讀檔與修改。

## 前置需求

- Python 3.12+。
- 已啟動 OpenAI-compatible FastContext model endpoint。

安裝本 package 時會從 Microsoft 官方 source 的固定版本一併安裝
FastContext，不需要額外 clone 或執行 `uv tool install`。

## 安裝本 MCP Server

```bash
git clone https://github.com/Jakevin/fastcontext-agent-tools
cd fastcontext-agent-tools
python -m pip install -e .
```

如果 `fastcontext-mcp` 不在 `PATH`，請用 `python -m fastcontext_mcp` 啟動。

## 環境變數

```bash
export BASE_URL="http://127.0.0.1:11434/v1"      # Ollama（建議）
export MODEL="fc-q4-nothink-16k:latest"
export API_KEY="ollama"
export FASTCONTEXT_ALLOWED_ROOTS="/path/to/repos"
```

`FASTCONTEXT_ALLOWED_ROOTS` 是安全白名單。MCP server 只會允許探索這些目錄底下的 repo。多個路徑請用系統的 `os.pathsep` 分隔：macOS/Linux 是 `:`，Windows 是 `;`。

## MCP 設定範例

```json
{
  "mcpServers": {
    "fastcontext": {
      "command": "python",
      "args": ["-m", "fastcontext_mcp"],
      "env": {
        "BASE_URL": "http://127.0.0.1:11434/v1",
        "MODEL": "fc-q4-nothink-16k:latest",
        "API_KEY": "ollama",
        "FASTCONTEXT_ALLOWED_ROOTS": "/path/to/repos",
        "FC_TEMPERATURE": "0.2",
        "FASTCONTEXT_REROOT_PATHS": "1",
        "FASTCONTEXT_EXPLORE_RETRIES": "2"
      }
    }
  }
}
```

## 工具

- `fastcontext_health`：檢查內建 FastContext module、endpoint 變數與 repo allowlist。
- `fastcontext_explore`：送出自然語言探索 query，回傳 citations 與 raw output。
- `fastcontext_explore_with_trace`：同上，但另外寫出 FastContext trajectory JSONL。

## 建議使用方式

適合用在：

- 不熟悉的中大型 codebase。
- 需要先找出功能入口、錯誤路徑、測試位置。
- 主 agent 不應該把大量 grep/read 歷史塞進自己的 context。

不適合用在：

- 已經知道要改哪個檔案。
- 很小的單檔問題。
- 需要直接修改檔案的任務。FastContext 只負責找 context。

給 LLM agent 的一句話：

> 請安裝 `https://github.com/Jakevin/fastcontext-agent-tools`；安裝 package 時會一併安裝 Microsoft FastContext。把 `python -m fastcontext_mcp` 設成 stdio MCP server，設定 `BASE_URL`、`MODEL`、`API_KEY`、`FASTCONTEXT_ALLOWED_ROOTS`，並啟用 `skills/fastcontext-explorer`。
