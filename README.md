# fixturefmt

Sports fixtures show up in whatever shape whoever typed them last used:
`Man Utd v Spurs, 12/9/2026 15:00` next to `Wolves - Chelsea, 2026-09-13
17:30`, abbreviations, inconsistent separators, dates in either order.
fixturefmt reads that and prints a single consistent line per fixture.

## Usage

From a file:

```
$ cat fixtures.txt
Man Utd v Spurs, 12/9/2026 15:00
Wolves - Chelsea, 2026-09-13 17:30
forest @ man city

$ python -m fixturefmt fixtures.txt
2026-09-12 15:00  Manchester United vs Tottenham Hotspur
2026-09-13 17:30  Wolverhampton Wanderers vs Chelsea
TBD  Nottingham Forest vs Manchester City
```

From stdin, which is the more common case in practice (pasting a fixture
list straight from a chat or clipboard):

```
$ pbpaste | python -m fixturefmt
```

Lines that start with `#` are treated as comments and skipped. Lines that
can't be parsed are reported on stderr with their line number, and the rest
of the input is still processed.

## Input format

One fixture per line: two team names separated by `vs`, `v`, `@` or `-`,
followed by zero or more fields separated by a comma or `|`. Each trailing
field can be a date/time or a competition name, in either order - whichever
fields parse as a date become the kickoff, everything else is kept as
competition text and printed in parentheses. If no date/time is given the
fixture is printed with `TBD`; if no competition is given it's left out.

```
$ echo "Man Utd v Spurs, Premier League, 12/9/2026 15:00" | python -m fixturefmt
2026-09-12 15:00  Manchester United vs Tottenham Hotspur  (Premier League)
```

Team name normalisation currently covers a small, hand-picked set of common
abbreviations (see `TEAM_ALIASES` in `fixturefmt/formatter.py`). Anything not
in that table is title-cased and passed through as-is.

## Status

Early skeleton. Date parsing only covers a handful of formats and the team
alias table is short — both grow as real input surfaces gaps.
