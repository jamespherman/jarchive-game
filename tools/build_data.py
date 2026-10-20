#!/usr/bin/env python3
"""Build the private clue file that the game loads.

Downloads the J! Archive-derived clue dataset maintained at
https://github.com/jwolle1/jeopardy_clue_dataset, cleans it, and writes
data/jeopardy-clues.json.gz. That file is what you copy to each device and
load with the game's "Load clue file" button. It must NOT be committed to the
public repo (data/ is in .gitignore).

Usage:  python3 tools/build_data.py
"""

import csv
import gzip
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "source"
OUT = ROOT / "data" / "jeopardy-clues.json.gz"
BASE_URL = "https://raw.githubusercontent.com/jwolle1/jeopardy_clue_dataset/main/"
SOURCES = ["combined_season1-42.tsv", "extra_matches.tsv"]

# Clue values doubled on this date; earlier values are scaled x2 so all eras compare.
DOUBLING_DATE = "2001-11-26"

ROUND_CODES = {"1": 1, "2": 2, "3": 3, "single": 1, "double": 2, "final": 3, "triple": 4}

# Show types for the filter, checked in order; the first match wins.
SHOW_TYPES = [
    ("regular", "Regular games", None),
    ("toc", "Tournament of Champions",
     r"(?<!Ultimate )Tournament of Champions"),
    ("college", "College Championship", r"College Championship"),
    ("teen", "Teen & High School", r"Teen|High School"),
    ("kids", "Kids & Back to School", r"Kids|Back to School"),
    ("teachers", "Teachers Tournament", r"Teachers"),
    ("celebrity", "Celebrity & Power Players", r"Celebrity|Power Players"),
    ("champions", "Champions events (Masters, GOAT, Invitational, Wildcard, ...)",
     r"Ultimate Tournament|Masters|Greatest of All Time|Super Jeopardy|Battle of the Decades"
     r"|All-Star|Anniversary|Invitational|Wildcard|Second Chance"),
    ("other", "Other specials (Professors, Seniors, International, ...)", r"."),
]


def show_type(notes):
    if not notes.strip():
        return 0
    for i, (_, _, pattern) in enumerate(SHOW_TYPES):
        if pattern and re.search(pattern, notes):
            return i
    return len(SHOW_TYPES) - 1


def clean(text):
    text = re.sub(r"\\(.)", r"\1", text)  # \" -> "  and  \' -> '
    return html.unescape(text).strip()


def fetch(name):
    path = CACHE / name
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {name} ...")
        urllib.request.urlretrieve(BASE_URL + name, path)
    return path


def main():
    games = {}        # (air_date, notes) -> game index
    game_cols = {"date": [], "type": [], "note": []}
    notes_list, notes_idx = [], {}
    cats, cat_idx = [], {}
    comments, comment_idx = [""], {"": 0}
    clues = {"g": [], "r": [], "v": [], "dd": [], "c": [], "cm": [], "q": [], "a": []}

    def intern(value, lst, idx):
        if value not in idx:
            idx[value] = len(lst)
            lst.append(value)
        return idx[value]

    for name in SOURCES:
        is_extra = name.startswith("extra")
        with open(fetch(name), newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                clue, response = clean(row["answer"]), clean(row["question"])
                if not clue or not response or row["round"] not in ROUND_CODES:
                    continue
                date, notes = row["air_date"], row["notes"].strip()
                key = (date, notes)
                if key not in games:
                    games[key] = len(game_cols["date"])
                    game_cols["date"].append(date)
                    game_cols["type"].append(show_type(notes))
                    game_cols["note"].append(intern(notes, notes_list, notes_idx))
                rnd = ROUND_CODES[row["round"]]
                value = int(row["clue_value"] or 0)
                if not is_extra and date < DOUBLING_DATE:
                    value *= 2
                clues["g"].append(games[key])
                clues["r"].append(rnd)
                clues["v"].append(value)
                clues["dd"].append(1 if int(row["daily_double_value"] or 0) > 0 else 0)
                clues["c"].append(intern(clean(row["category"]), cats, cat_idx))
                clues["cm"].append(intern(clean(row["comments"]), comments, comment_idx))
                clues["q"].append(clue)
                clues["a"].append(response)

    data = {
        "format": "jarchive-game-clues",
        "version": 1,
        "source": "github.com/jwolle1/jeopardy_clue_dataset (derived from j-archive.com)",
        "showTypes": [{"id": i, "key": key, "label": label}
                      for i, (key, label, _) in enumerate(SHOW_TYPES)],
        "games": game_cols,
        "notes": notes_list,
        "categories": cats,
        "comments": comments,
        "clues": clues,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.open(OUT, "wb", compresslevel=9) as f:
        f.write(raw)

    counts = [0] * len(SHOW_TYPES)
    for g in clues["g"]:
        counts[game_cols["type"][g]] += 1
    print(f"{len(clues['q']):,} clues from {len(game_cols['date']):,} games")
    for (_, label, _), n in zip(SHOW_TYPES, counts):
        print(f"  {n:>8,}  {label}")
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB; {len(raw) / 1e6:.1f} MB uncompressed)")


if __name__ == "__main__":
    sys.exit(main())
