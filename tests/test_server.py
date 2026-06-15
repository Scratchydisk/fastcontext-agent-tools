from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock

from fastcontext_mcp import runtime
from fastcontext_mcp.runtime import (
    health,
    parse_citations,
    resolve_repo_path,
    run_fastcontext,
)
from fastcontext_mcp.server import handle_request


class ServerTests(unittest.TestCase):
    def test_parse_citations_from_final_answer(self) -> None:
        text = """
        notes
        <final_answer>
        src/router.py:42-58
        tests/test_router.py:101
        </final_answer>
        """
        citations = parse_citations(text)
        self.assertEqual(len(citations), 2)
        self.assertEqual(citations[0].path, "src/router.py")
        self.assertEqual(citations[0].start_line, 42)
        self.assertEqual(citations[0].end_line, 58)
        self.assertEqual(citations[1].end_line, 101)

    def test_repo_path_must_be_under_allowed_roots(self) -> None:
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as other:
            with mock.patch.dict(os.environ, {"FASTCONTEXT_ALLOWED_ROOTS": root}):
                with self.assertRaises(Exception):
                    resolve_repo_path(other)

    def test_tools_list(self) -> None:
        response = handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        assert response is not None
        names = {tool["name"] for tool in response["result"]["tools"]}
        self.assertIn("fastcontext_health", names)
        self.assertIn("fastcontext_explore", names)

    def test_health_tool_returns_json_text(self) -> None:
        response = handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "fastcontext_health", "arguments": {}},
            }
        )
        assert response is not None
        text = response["result"]["content"][0]["text"]
        payload = json.loads(text)
        self.assertIn("fastcontext_module", payload)

    def test_health_uses_bundled_fastcontext_module_without_path_cli(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"BASE_URL": "https://example.test/v1", "MODEL": "fastcontext"},
            clear=True,
        ):
            with mock.patch.object(runtime, "_fastcontext_available", return_value=True):
                payload = health()

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["fastcontext_module"], "fastcontext.cli")

    def test_run_fastcontext_uses_current_python_module(self) -> None:
        completed = CompletedProcess(
            args=[],
            returncode=0,
            stdout="<final_answer>\nsrc/app.py:1-3\n</final_answer>\n",
            stderr="",
        )
        with tempfile.TemporaryDirectory() as root:
            with mock.patch.dict(os.environ, {"FASTCONTEXT_ALLOWED_ROOTS": root}):
                with mock.patch.object(runtime, "_fastcontext_available", return_value=True):
                    with mock.patch(
                        "fastcontext_mcp.runtime.subprocess.run",
                        return_value=completed,
                    ) as run:
                        result = run_fastcontext(
                            {"repo_path": root, "query": "Locate app"},
                        )

        self.assertTrue(result["ok"])
        command = run.call_args.args[0]
        self.assertEqual(command[:3], [sys.executable, "-m", "fastcontext.cli"])

    def test_relative_allowed_root_defaults_to_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            cwd = Path(root)
            child = cwd / "repo"
            child.mkdir()
            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch("os.getcwd", return_value=str(cwd)):
                    self.assertEqual(resolve_repo_path(str(child)), child.resolve())


if __name__ == "__main__":
    unittest.main()
