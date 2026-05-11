from __future__ import annotations

import cli


def test_workflows_run_defaults_to_dry_run(monkeypatch):
    called = {}

    def fake_dry(args):
        called["dry"] = args
        return 0

    def fake_run(args):
        called["run"] = args
        return 0

    monkeypatch.setattr(cli, "cmd_dry_run", fake_dry)
    monkeypatch.setattr(cli, "cmd_run", fake_run)

    rc = cli.cmd_workflows(["run", "Build", "thing"])

    assert rc == 0
    assert called["dry"] == ["Build", "thing"]
    assert "run" not in called


def test_workflows_run_execute_flag(monkeypatch):
    called = {}

    def fake_dry(args):
        called["dry"] = args
        return 0

    def fake_run(args):
        called["run"] = args
        return 0

    monkeypatch.setattr(cli, "cmd_dry_run", fake_dry)
    monkeypatch.setattr(cli, "cmd_run", fake_run)

    rc = cli.cmd_workflows(["run", "--execute", "Ship", "release"])

    assert rc == 0
    assert called["run"] == ["Ship", "release"]


def test_runs_list_bad_output_mode(capsys):
    rc = cli.cmd_runs(["list", "--output", "xml"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "--output must be one of" in err


def test_schedules_unknown_subcommand(capsys):
    rc = cli.cmd_schedules(["oops"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "usage: apotheon schedules" in err


def test_parse_output_mode_json_flag():
    mode, rest = cli._parse_output_mode(["--json", "--limit", "5"])
    assert mode == "json"
    assert rest == ["--limit", "5"]
