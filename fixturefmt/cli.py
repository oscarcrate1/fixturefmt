"""Command-line entry point: fixturefmt [file ...]

With no file arguments, reads fixture lines from stdin. This is the case
that matters most in practice, since fixtures usually get pasted in rather
than saved to a file first.
"""

from __future__ import annotations

import argparse
import sys
from typing import Iterable, TextIO

from .formatter import FixtureParseError, parse_line


def iter_sources(paths: list[str]) -> Iterable[tuple[str, TextIO]]:
    if not paths:
        yield "<stdin>", sys.stdin
        return
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            yield path, handle


def process(label: str, handle: TextIO, out: TextIO) -> int:
    error_count = 0
    for lineno, raw_line in enumerate(handle, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            fixture = parse_line(line)
        except FixtureParseError as exc:
            print(f"{label}:{lineno}: {exc}", file=sys.stderr)
            error_count += 1
            continue
        print(fixture.format(), file=out)
    return error_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Normalise messy sports fixture text into a consistent format."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="fixture files to read; omit to read from stdin",
    )
    args = parser.parse_args(argv)

    error_count = 0
    for label, handle in iter_sources(args.files):
        error_count += process(label, handle, sys.stdout)

    return 1 if error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
