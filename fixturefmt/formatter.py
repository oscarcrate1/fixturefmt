"""Turn messy, hand-typed fixture lines into a consistent line format.

Real inputs I've seen come from group chats, printed schedules retyped by
hand, and half-finished spreadsheets: team names abbreviated inconsistently,
separators that vary between "vs", "v", "-" and "@", and dates in whatever
order the person typing them grew up with.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

# Only the aliases I've personally needed to fix so far. This grows as new
# messy spellings show up in real input rather than being guessed up front.
TEAM_ALIASES = {
    "man utd": "Manchester United",
    "man u": "Manchester United",
    "man city": "Manchester City",
    "spurs": "Tottenham Hotspur",
    "tottenham": "Tottenham Hotspur",
    "wolves": "Wolverhampton Wanderers",
    "forest": "Nottingham Forest",
    "nffc": "Nottingham Forest",
}

# Order matters: try the most specific separators before the bare hyphen,
# since a hyphenated team name (rare, but exists) would otherwise get split.
_TEAM_SPLIT_RE = re.compile(r"\s+(?:vs\.?|v\.?|@)\s+|\s+-\s+", re.IGNORECASE)

_FIELD_SPLIT_RE = re.compile(r"\s*[|,]\s*")

# Formats seen in the wild, tried in order until one matches.
_DATETIME_FORMATS = (
    "%Y-%m-%d %H:%M",
    "%d/%m/%Y %H:%M",
    "%d/%m/%y %H:%M",
    "%d-%m-%Y %H:%M",
    "%Y-%m-%d",
    "%d/%m/%Y",
)


class FixtureParseError(ValueError):
    """Raised when a line can't be turned into a Fixture."""


@dataclass(frozen=True)
class Fixture:
    home: str
    away: str
    kickoff: datetime | None
    competition: str | None = None

    def format(self) -> str:
        when = self.kickoff.strftime("%Y-%m-%d %H:%M") if self.kickoff else "TBD"
        line = f"{when}  {self.home} vs {self.away}"
        if self.competition:
            line += f"  ({self.competition})"
        return line


def normalise_team(name: str) -> str:
    key = name.strip().lower()
    if key in TEAM_ALIASES:
        return TEAM_ALIASES[key]
    return " ".join(word.capitalize() for word in name.strip().split())


def parse_datetime(text: str) -> datetime:
    text = text.strip()
    for fmt in _DATETIME_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    raise FixtureParseError(f"unrecognised date/time: {text!r}")


def parse_line(line: str) -> Fixture:
    """Parse one fixture line such as "Man Utd v Spurs, Premier League, 12/9/2026 15:00".

    Fields after the teams can appear in either order - a date/time and a
    competition name aren't distinguishable by position alone, so each
    trailing field is tried as a date first and kept as competition text if
    that fails.
    """
    fields = _FIELD_SPLIT_RE.split(line.strip())
    teams_part = fields[0]

    match = _TEAM_SPLIT_RE.split(teams_part)
    if len(match) != 2:
        raise FixtureParseError(f"couldn't find two teams in: {teams_part!r}")
    home, away = (normalise_team(t) for t in match)

    kickoff = None
    competition_parts = []
    for field in fields[1:]:
        field = field.strip()
        if not field:
            continue
        try:
            kickoff = parse_datetime(field)
        except FixtureParseError:
            competition_parts.append(field)
    competition = ", ".join(competition_parts) if competition_parts else None

    return Fixture(home=home, away=away, kickoff=kickoff, competition=competition)
