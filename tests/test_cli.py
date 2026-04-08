from pathlib import Path

from docflow_ai import cli


def _input_factory(values: list[str]):
    iterator = iter(values)
    return lambda _prompt: next(iterator)


def test_prompt_mode_retries_until_valid() -> None:
    mode = cli._prompt_mode(input_fn=_input_factory(["x", "paired"]))
    assert mode == "paired"


def test_prompt_top_k_blank_and_valid_values() -> None:
    assert cli._prompt_top_k(input_fn=_input_factory([""])) is None
    assert cli._prompt_top_k(input_fn=_input_factory(["4"])) == 4


def test_prompt_yes_no_accepts_yes_and_no() -> None:
    assert cli._prompt_yes_no("Run", input_fn=_input_factory(["yes"])) is True
    assert cli._prompt_yes_no("Run", input_fn=_input_factory(["n"])) is False


def test_interactive_main_single_run(monkeypatch) -> None:
    calls: list[tuple[Path, Path, str, int | None]] = []

    async def fake_run(cv_dir: Path, job_dir: Path, mode: str, top_k: int | None) -> None:
        calls.append((cv_dir, job_dir, mode, top_k))

    monkeypatch.setattr(cli, "run", fake_run)
    monkeypatch.setattr(cli, "bootstrap_dataset", lambda *_args: (0, 0))

    responses = _input_factory([
        "",  # keep default cv dir
        "",  # keep default job dir
        "n",  # no bootstrap
        "c",  # cross mode
        "3",  # top-k
        "n",  # do not run again
    ])
    monkeypatch.setattr("builtins.input", responses)

    cli.interactive_main(Path("data/cv"), Path("data/jobs"))

    assert calls == [(Path("data/cv"), Path("data/jobs"), "cross", 3)]
