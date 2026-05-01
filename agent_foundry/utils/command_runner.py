"""Subprocess utility with consistent error semantics."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Sequence

from agent_foundry.core.errors import ExternalCommandError


@dataclass(frozen=True)
class CommandResult:
    stdout: str
    stderr: str
    returncode: int


def run_command(
    args: Sequence[str],
    *,
    check: bool = True,
    capture_output: bool = True,
) -> CommandResult:
    result = subprocess.run(
        list(args),
        capture_output=capture_output,
        text=True,
        check=False,
    )
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    if check and result.returncode != 0:
        rendered = " ".join(args)
        raise ExternalCommandError(
            f"Command failed ({result.returncode}): {rendered}\n{stderr or stdout}".rstrip()
        )
    return CommandResult(stdout=stdout, stderr=stderr, returncode=result.returncode)
