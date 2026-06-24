import json

import pytest

from rpd_generator.doe2_worker import api


class FakeStdin:
    def __init__(self):
        self.writes = []
        self.flush_count = 0

    def write(self, value):
        self.writes.append(value)

    def flush(self):
        self.flush_count += 1


class FakeStdout:
    def __init__(self, lines):
        self.lines = list(lines)

    def readline(self):
        return self.lines.pop(0) if self.lines else ""


class FakeStderr:
    def __init__(self, text):
        self.text = text

    def read(self):
        return self.text


class FakeProcess:
    def __init__(self, *, stdout_lines=None, stderr_text="", poll_result=None):
        self.stdin = FakeStdin()
        self.stdout = FakeStdout(stdout_lines or [])
        self.stderr = FakeStderr(stderr_text)
        self.poll_result = poll_result
        self.terminated = False

    def poll(self):
        return self.poll_result

    def terminate(self):
        self.terminated = True


def test_ensure_worker_reuses_running_process(monkeypatch, tmp_path):
    py32 = tmp_path / "python.exe"
    py32.write_text("")
    worker = tmp_path / "bdl_worker.py"
    process = FakeProcess()
    popen_calls = []

    def fake_popen(cmd, **kwargs):
        popen_calls.append((cmd, kwargs))
        return process

    monkeypatch.setattr(api.sys, "frozen", False, raising=False)
    monkeypatch.setattr(api, "PY32", py32)
    monkeypatch.setattr(api, "WORKER", worker)
    monkeypatch.setattr(api, "_worker_proc", None)
    monkeypatch.setattr(api.subprocess, "Popen", fake_popen)

    assert api._ensure_worker() is process
    assert api._ensure_worker() is process

    assert len(popen_calls) == 1
    assert popen_calls[0][0] == [str(py32), str(worker)]
    assert popen_calls[0][1]["stdin"] == api.subprocess.PIPE
    assert popen_calls[0][1]["text"] is True


def test_ensure_worker_falls_back_to_bundled_exe_when_python32_is_absent(
    monkeypatch, tmp_path
):
    worker_exe = tmp_path / "bdl_worker.exe"
    worker_exe.write_text("")
    popen_calls = []

    def fake_popen(cmd, **kwargs):
        popen_calls.append(cmd)
        return FakeProcess()

    monkeypatch.setattr(api.sys, "frozen", False, raising=False)
    monkeypatch.setattr(api, "PY32", tmp_path / "missing_python.exe")
    monkeypatch.setattr(api, "WORKER_EXE", worker_exe)
    monkeypatch.setattr(api, "_worker_proc", None)
    monkeypatch.setattr(api.subprocess, "Popen", fake_popen)

    api._ensure_worker()

    assert popen_calls == [[str(worker_exe)]]


def test_ensure_worker_raises_when_no_development_worker_runtime_exists(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(api.sys, "frozen", False, raising=False)
    monkeypatch.setattr(api, "PY32", tmp_path / "missing_python.exe")
    monkeypatch.setattr(api, "WORKER_EXE", tmp_path / "missing_worker.exe")
    monkeypatch.setattr(api, "_worker_proc", None)

    with pytest.raises(FileNotFoundError, match="DOE-2 worker runtime not found"):
        api._ensure_worker()


def test_rpc_writes_payload_and_returns_success_response(monkeypatch):
    process = FakeProcess(stdout_lines=['{"status": "ok", "results": [1, 2]}\n'])

    monkeypatch.setattr(api, "_ensure_worker", lambda: process)

    assert api._rpc({"cmd": "get", "value": 1}) == {
        "status": "ok",
        "results": [1, 2],
    }
    assert json.loads(process.stdin.writes[0]) == {"cmd": "get", "value": 1}
    assert process.stdin.writes[0].endswith("\n")
    assert process.stdin.flush_count == 1


def test_rpc_raises_worker_error_response(monkeypatch):
    process = FakeProcess(
        stdout_lines=['{"status": "error", "error": "bad request"}\n']
    )

    monkeypatch.setattr(api, "_ensure_worker", lambda: process)

    with pytest.raises(RuntimeError, match="Worker error: bad request"):
        api._rpc({"cmd": "bad"})


def test_rpc_includes_stderr_when_worker_returns_no_output(monkeypatch):
    process = FakeProcess(stdout_lines=[], stderr_text="traceback text")

    monkeypatch.setattr(api, "_ensure_worker", lambda: process)

    with pytest.raises(RuntimeError, match="traceback text"):
        api._rpc({"cmd": "get"})


def test_public_api_wrappers_send_expected_commands(monkeypatch):
    calls = []

    def fake_rpc(payload):
        calls.append(payload)
        if payload["cmd"] == "get_multiple":
            return {"results": ["A", "B"]}
        if payload["cmd"] == "get_single":
            return {"results": "A"}
        return {"status": "ok"}

    monkeypatch.setattr(api, "_rpc", fake_rpc)

    assert api.process_inp(path="model.inp") == {"status": "ok"}
    assert api.get_multiple_results_32(
        d2_result_dll="dll",
        doe2_data_dir="data",
        project_fname="project",
        requests=[{"entry_id": 1}],
    ) == ["A", "B"]
    assert (
        api.get_string_result_32(
            d2_result_dll="dll",
            doe2_data_dir="data",
            project_fname="project",
            entry_id=1,
            report_key="LV-B",
            row_key="row",
        )
        == "A"
    )

    assert calls == [
        {"cmd": "process_inp", "path": "model.inp"},
        {
            "cmd": "get_multiple",
            "d2_result_dll": "dll",
            "doe2_data_dir": "data",
            "project_fname": "project",
            "requests": [{"entry_id": 1}],
        },
        {
            "cmd": "get_single",
            "d2_result_dll": "dll",
            "doe2_data_dir": "data",
            "project_fname": "project",
            "entry_id": 1,
            "report_key": "LV-B",
            "row_key": "row",
        },
    ]


def test_shutdown_worker_terminates_running_process_and_clears_singleton(monkeypatch):
    process = FakeProcess()

    monkeypatch.setattr(api, "_worker_proc", process)
    monkeypatch.setattr(api, "_rpc", lambda payload: None)

    api.shutdown_worker()

    assert process.terminated is True
    assert api._worker_proc is None
