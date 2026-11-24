#!/usr/bin/env python3
"""Fail if a pull request's title or description names a private host, an
internal host or a private path.

The workflow passes the title and body through the PR_TITLE and PR_BODY
environment variables (from github.event.pull_request, never interpolated
into a shell command). They are written to a private temporary file and
scanned with this repository's own privacy checker (scripts/check_privacy.py scan_patterns).
Only finding kinds and line numbers are reported, never the matched text.
"""
import importlib.util, os, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _checker():
    spec = importlib.util.spec_from_file_location('repo_privacy_checker', ROOT / 'scripts/check_privacy.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scan_file(path):
    """Return the checker's findings for one file as 'line: kind' strings."""
    checker = _checker()
    return list(checker.scan_patterns(path.read_bytes(), path.name))


def pr_text(env):
    return (env.get('PR_TITLE') or '') + '\n\n' + (env.get('PR_BODY') or '') + '\n'


def main(env=None):
    env = os.environ if env is None else env
    if 'PR_TITLE' not in env or 'PR_BODY' not in env:
        print('PR_TITLE and PR_BODY must both be set', file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix='pr-text-') as tmp:
        os.chmod(tmp, 0o700)
        path = Path(tmp, 'pull-request.md')
        path.write_text(pr_text(env), encoding='utf-8')
        try:
            findings = scan_file(path)
        except Exception as error:  # fail closed
            findings = ['checker error: %s' % type(error).__name__]
    if findings:
        for finding in findings:
            print(str(finding).replace(tmp, '<pr-text>'), file=sys.stderr)
        print('PR title/description privacy check failed (%d finding(s)). '
              'Use role names such as "HPC host" or "workstation".' % len(findings), file=sys.stderr)
        return 1
    print('PR title/description privacy check passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
