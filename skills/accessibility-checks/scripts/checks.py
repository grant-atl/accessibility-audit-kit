#!/usr/bin/env python3
"""Run an explicitly configured project check; optionally receive Claude hook JSON."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile

CONFIG = ".accessibility-checks.json"
TRUST = "accessibility-audit-kit-trust.json"
MAX_BYTES = 65536


class CheckError(Exception):
    """A fixed, non-sensitive diagnostic that is safe to show in hook output."""


def git_path(cwd, argument):
    # Ambient Git overrides must not select a different project's config/trust.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    result = subprocess.run(
        ["git", "-C", str(cwd), "rev-parse", argument],
        capture_output=True, timeout=5, env=env,
    )
    if result.returncode:
        raise CheckError("A Git working tree is required.")
    return Path(os.fsdecode(result.stdout.removesuffix(b"\n"))).resolve()


def project_root(cwd):
    cwd = Path(cwd).resolve(strict=True)
    root = git_path(cwd, "--show-toplevel")
    if not cwd.is_dir() or not cwd.is_relative_to(root):
        raise CheckError("The project directory is outside its Git working tree.")
    return root


def load_config(root):
    path = root / CONFIG
    if path.is_symlink() or not path.is_file():
        raise CheckError("Create a regular .accessibility-checks.json file at the Git root first.")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise CheckError("The accessibility check configuration is too large.")
    try:
        config = json.loads(raw)
    except (ValueError, UnicodeError):
        raise CheckError("The accessibility check configuration must be valid JSON.") from None
    if not isinstance(config, dict) or set(config) - {"command", "timeout_seconds", "claude"}:
        raise CheckError("Allowed configuration keys: command, timeout_seconds, claude.")
    command = config.get("command")
    if (not isinstance(command, list) or not 1 <= len(command) <= 128
            or any(not isinstance(arg, str) or "\0" in arg for arg in command)
            or not command[0].strip()):
        raise CheckError("command must be a nonempty JSON array of argument strings.")
    timeout = config.get("timeout_seconds", 30)
    if type(timeout) is not int or not 1 <= timeout <= 120:
        raise CheckError("timeout_seconds must be an integer from 1 through 120.")
    if type(config.get("claude", False)) is not bool:
        raise CheckError("claude must be true or false.")
    digest = hashlib.sha256(str(root).encode() + b"\0" + raw).hexdigest()
    return config, timeout, digest


def trust_path(root):
    return git_path(root, "--absolute-git-dir") / TRUST


def execute(root, config, timeout, quiet=False):
    # POSIX process groups let a timed-out check's ordinary children be stopped too.
    if os.name != "posix":
        raise CheckError("This runner requires macOS, Linux, or WSL.")
    with subprocess.Popen(
        config["command"], cwd=root, stdin=subprocess.DEVNULL, shell=False,
        stdout=subprocess.DEVNULL if quiet else None,
        stderr=subprocess.DEVNULL if quiet else None, start_new_session=True,
    ) as process:
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            raise CheckError("The accessibility check timed out; no pass was recorded.") from None
    return code if code >= 0 else 128 - code


def claude_hook():
    raw = sys.stdin.buffer.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise CheckError("The accessibility hook input is too large; check was not run.")
    try:
        event = json.loads(raw)
    except (ValueError, UnicodeError):
        raise CheckError("The accessibility hook received invalid JSON; check was not run.") from None
    if not isinstance(event, dict):
        raise CheckError("The accessibility hook input must be an object.")
    if event.get("hook_event_name") != "PostToolUse" or event.get("tool_name") not in ("Edit", "Write"):
        return 0
    cwd = event.get("cwd")
    tool_input = event.get("tool_input")
    file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if not isinstance(cwd, str) or not Path(cwd).is_absolute():
        raise CheckError("The accessibility hook requires an absolute project directory.")
    if not isinstance(file_path, str) or not Path(file_path).is_absolute():
        raise CheckError("The accessibility hook requires an absolute edited-file path.")
    try:
        root = project_root(cwd)
    except CheckError:
        return 0  # Plugin installation does not opt non-project directories in.
    if not Path(file_path).resolve().is_relative_to(root) or not (root / CONFIG).exists():
        return 0
    marker = trust_path(root)
    if not marker.exists():
        return 0  # A cloned configuration cannot authorize command execution.
    config, timeout, digest = load_config(root)
    if not config.get("claude", False):
        return 0
    if marker.is_symlink() or not marker.is_file():
        raise CheckError("The accessibility trust record must be a regular file.")
    with marker.open("rb") as stream:
        trusted_digest = stream.read(66)
    if trusted_digest != (digest + "\n").encode():
        raise CheckError("Accessibility hook configuration changed. Review it and run trust again before automatic checks.")
    code = execute(root, config, timeout, quiet=True)
    if code:
        raise CheckError("The configured accessibility check failed. Run checks.py run locally for details; do not claim the check passed.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("run", "trust", "revoke"):
        command = sub.add_parser(action)
        command.add_argument("--project", default=".", help="Any directory in the target Git working tree")
    sub.add_parser("claude", help="Read a PostToolUse event from stdin (plugin use)")
    args = parser.parse_args()
    try:
        if args.action == "claude":
            return claude_hook()
        root = project_root(args.project)
        if args.action == "revoke":
            trust_path(root).unlink(missing_ok=True)
            print("Automatic accessibility checks revoked for this working tree.")
            return 0
        config, timeout, digest = load_config(root)
        if args.action == "run":
            return execute(root, config, timeout)
        if not config.get("claude", False):
            raise CheckError("Set claude to true before trusting automatic checks.")
        marker = trust_path(root)
        # The trust record is local Git metadata, never a clonable project file.
        with tempfile.NamedTemporaryFile(mode="w", dir=marker.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(digest + "\n")
        try:
            os.replace(temporary, marker)
        finally:
            temporary.unlink(missing_ok=True)
        print("Automatic accessibility checks enabled for this working tree and exact configuration.")
        return 0
    except CheckError as error:
        print(str(error), file=sys.stderr)
    except (OSError, ValueError, RecursionError, subprocess.SubprocessError):
        print("Accessibility checks could not run. Verify Git, the configuration, interpreter, and command locally.", file=sys.stderr)
    return 2 if args.action == "claude" else 1


if __name__ == "__main__":
    sys.exit(main())
