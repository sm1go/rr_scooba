"""Aggregate the multi-agent ideation scores.

Reads
  docs/02-ideation/round-1-proposals/*.md       raw features (<ROLE>-NN) + self-assessment
  docs/02-ideation/round-2-reviews/*.md         peer scores (J1-J3) + ranked top-10 picks
  docs/03-product/scoring/feature-mapping.csv   optional: raw_id -> f_id (consolidated catalog)
  docs/02-ideation/round-3-votes/*.md           optional: 100-point allocations per F-ID
Writes CSV files and summary.md into docs/03-product/scoring/.

Weighted score = 0.45*J1 + 0.35*J2 + 0.20*J3 (official Junction judging weights).
Only peer scores count: a reviewer's scores for features of their own role are ignored.

Usage: python scripts/aggregate_scores.py
"""
from __future__ import annotations

import csv
import re
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDEATION = ROOT / "docs" / "02-ideation"
OUT = ROOT / "docs" / "03-product" / "scoring"
WEIGHTS = (0.45, 0.35, 0.20)
ROLES = ("STR", "PM", "UX", "TECH", "RAI", "TAL")

RAW_ID = re.compile(r"\b(?:" + "|".join(ROLES) + r")-\d{2}\b")
F_ID = re.compile(r"\bF\d{2}\b")
HEADING = re.compile(r"^###\s+((?:" + "|".join(ROLES) + r")-\d{2})\s*[:.\-–—]\s*(.+?)\s*$")
FIELD = re.compile(r"^\s*[-*]\s*\*\*(.+?):?\*\*:?\s*(.*)$")
SELF = re.compile(
    r"J1\s*[:=]?\s*(\d(?:\.\d+)?).*?J2\s*[:=]?\s*(\d(?:\.\d+)?).*?J3\s*[:=]?\s*(\d(?:\.\d+)?)"
)
LIST_ITEM = re.compile(r"^\s*(?:\d+[.)]|[-*]|\|)\s*")


def weighted(j1: float, j2: float, j3: float) -> float:
    return WEIGHTS[0] * j1 + WEIGHTS[1] * j2 + WEIGHTS[2] * j3


def section(text: str, title_prefix: str) -> str:
    """Body of the first '## ' section whose title starts with title_prefix."""
    body, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip().lower().startswith(title_prefix.lower())
            continue
        if inside:
            body.append(line)
    return "\n".join(body)


def table_cells(line: str) -> list[str]:
    return [c.strip().strip("*_`").strip() for c in line.strip().strip("|").split("|")]


def author(fid: str) -> str:
    return fid.split("-")[0]


def fmt(x: float | None, digits: int = 2) -> str:
    return "" if x is None else f"{x:.{digits}f}"


def write_csv(name: str, header: list[str], rows: list[list]) -> None:
    with (OUT / name).open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def md_table(header: list[str], rows: list[list]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return lines


def parse_features() -> dict[str, dict]:
    features: dict[str, dict] = {}
    for path in sorted((IDEATION / "round-1-proposals").glob("*.md")):
        current = None
        for line in path.read_text(encoding="utf-8").splitlines():
            m = HEADING.match(line)
            if m:
                current = {"id": m.group(1), "name": m.group(2).strip(), "fields": {}}
                features[m.group(1)] = current
            elif line.startswith("#"):
                current = None
            elif current is not None and (f := FIELD.match(line)):
                current["fields"][f.group(1).strip().lower()] = f.group(2).strip()
    for feat in features.values():
        s = SELF.search(feat["fields"].get("self-assessment", ""))
        feat["self"] = tuple(float(x) for x in s.groups()) if s else None
    return features


def parse_reviews() -> tuple[dict[tuple[str, str], tuple[int, int, int]], dict[str, list[str]]]:
    scores: dict[tuple[str, str], tuple[int, int, int]] = {}
    top10: dict[str, list[str]] = {}
    for path in sorted((IDEATION / "round-2-reviews").glob("*.md")):
        reviewer = path.name.split("-")[0].upper()
        text = path.read_text(encoding="utf-8")
        for line in section(text, "3.").splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = table_cells(line)
            m = RAW_ID.search(cells[0]) if cells else None
            nums = [c for c in cells[1:] if re.fullmatch(r"[1-5]", c)]
            if not m or len(nums) < 3 or author(m.group(0)) == reviewer:
                continue
            scores.setdefault((reviewer, m.group(0)), tuple(int(x) for x in nums[:3]))
        picks: list[str] = []
        for line in section(text, "4.").splitlines():
            if LIST_ITEM.match(line) and (m := RAW_ID.search(line)) and m.group(0) not in picks:
                picks.append(m.group(0))
        top10[reviewer] = picks[:10]
    return scores, top10


def parse_votes() -> dict[str, dict[str, int]]:
    votes: dict[str, dict[str, int]] = {}
    for path in sorted((IDEATION / "round-3-votes").glob("*.md")):
        voter = path.name.split("-")[0].upper()
        alloc: dict[str, int] = defaultdict(int)
        for line in section(path.read_text(encoding="utf-8"), "points").splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = table_cells(line)
            m = F_ID.search(cells[0]) if cells else None
            nums = [c for c in cells[1:] if re.fullmatch(r"\d{1,3}", c)]
            if m and nums:
                alloc[m.group(0)] += int(nums[0])
        votes[voter] = dict(alloc)
    return votes


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    features = parse_features()
    scores, top10 = parse_reviews()
    report: list[str] = [
        "# Scoring summary (generated)",
        "",
        "Generated by `scripts/aggregate_scores.py`. Do not edit by hand.",
        "Weighted = 0.45·J1 + 0.35·J2 + 0.20·J3. Only peer scores count (self-scores excluded).",
        "Borda = 10 points for a reviewer's #1 pick … 1 point for #10.",
        "",
    ]

    write_csv(
        "raw-features.csv",
        ["id", "author", "name", "journey_stage", "primary_users", "pain_points", "prototype", "self_j1", "self_j2", "self_j3"],
        [
            [f["id"], author(f["id"]), f["name"], f["fields"].get("journey stage", ""),
             f["fields"].get("primary users", ""), f["fields"].get("pain points addressed", ""),
             f["fields"].get("48h prototype", "")[:1], *(f["self"] or ("", "", ""))]
            for f in features.values()
        ],
    )
    report.append(f"Raw features parsed: **{len(features)}** from {len({author(i) for i in features})} roles.")

    if not scores:
        report.append("\nNo Round 2 reviews found yet.")
        (OUT / "summary.md").write_text("\n".join(report) + "\n", encoding="utf-8")
        print("\n".join(report))
        return

    write_csv(
        "peer-scores.csv",
        ["reviewer", "feature_id", "j1", "j2", "j3", "weighted"],
        [[r, fid, *s, fmt(weighted(*s))] for (r, fid), s in sorted(scores.items())],
    )

    borda: dict[str, int] = defaultdict(int)
    mentions: dict[str, int] = defaultdict(int)
    for picks in top10.values():
        for rank, fid in enumerate(picks, start=1):
            borda[fid] += 11 - rank
            mentions[fid] += 1

    per_feature: dict[str, list[tuple[int, int, int]]] = defaultdict(list)
    for (_, fid), s in scores.items():
        per_feature[fid].append(s)

    summary = []
    for fid, feat in features.items():
        rows = per_feature.get(fid, [])
        w = [weighted(*s) for s in rows]
        mean_w = statistics.mean(w) if w else None
        self_w = weighted(*feat["self"]) if feat["self"] else None
        summary.append({
            "id": fid, "name": feat["name"], "author": author(fid), "n": len(rows),
            "j1": statistics.mean(s[0] for s in rows) if rows else None,
            "j2": statistics.mean(s[1] for s in rows) if rows else None,
            "j3": statistics.mean(s[2] for s in rows) if rows else None,
            "w": mean_w, "sd": statistics.pstdev(w) if len(w) > 1 else None,
            "mentions": mentions.get(fid, 0), "borda": borda.get(fid, 0), "self_w": self_w,
            "bias": (self_w - mean_w) if (self_w is not None and mean_w is not None) else None,
        })
    summary.sort(key=lambda r: (r["w"] or 0, r["borda"]), reverse=True)

    header = ["rank", "id", "name", "author", "n_reviews", "j1", "j2", "j3", "weighted", "sd", "top10_mentions", "borda", "self_weighted", "self_minus_peer"]
    rows = [[i, r["id"], r["name"], r["author"], r["n"], fmt(r["j1"]), fmt(r["j2"]), fmt(r["j3"]), fmt(r["w"]), fmt(r["sd"]), r["mentions"], r["borda"], fmt(r["self_w"]), fmt(r["bias"])] for i, r in enumerate(summary, start=1)]
    write_csv("feature-summary.csv", header, rows)
    report += ["", "## Raw features ranked by peer score", ""]
    report += md_table(["#", "ID", "Feature", "n", "J1", "J2", "J3", "Weighted", "SD", "Top-10", "Borda", "Self−peer"],
                       [[r[0], r[1], r[2], r[4], r[5], r[6], r[7], f"**{r[8]}**", r[9], r[10], r[11], r[13]] for r in rows])

    report += ["", "## Reviewer calibration (mean weighted score given: reviewer → author)", ""]
    calib = []
    for reviewer in ROLES:
        cells = []
        for auth in ROLES:
            vals = [weighted(*s) for (r, fid), s in scores.items() if r == reviewer and author(fid) == auth]
            cells.append(fmt(statistics.mean(vals)) if vals else "—")
        calib.append([reviewer, *cells])
    report += md_table(["Reviewer \\ Author", *ROLES], calib)

    report += ["", "## Coverage check", ""]
    for reviewer in sorted(top10):
        expected = {fid for fid in features if author(fid) != reviewer}
        missing = sorted(expected - {fid for (r, fid) in scores if r == reviewer})
        report.append(f"- {reviewer}: scored {len(expected) - len(missing)}/{len(expected)}"
                      + (f" — missing: {', '.join(missing)}" if missing else "") + f"; top-10 picks parsed: {len(top10[reviewer])}")

    mapping_path = OUT / "feature-mapping.csv"
    if mapping_path.exists():
        with mapping_path.open(encoding="utf-8") as fh:
            mapping = {row["raw_id"].strip(): row["f_id"].strip() for row in csv.DictReader(fh)}
        by_id = {r["id"]: r for r in summary}
        clusters: dict[str, list[str]] = defaultdict(list)
        for raw_id, f_id in mapping.items():
            clusters[f_id].append(raw_id)
        crow = []
        for f_id, members in clusters.items():
            ws = [by_id[m]["w"] for m in members if m in by_id and by_id[m]["w"] is not None]
            crow.append([f_id, len(members), " ".join(sorted(members)),
                         fmt(statistics.mean(ws)) if ws else "", fmt(max(ws)) if ws else "",
                         sum(by_id[m]["mentions"] for m in members if m in by_id),
                         sum(by_id[m]["borda"] for m in members if m in by_id)])
        crow.sort(key=lambda r: (float(r[3] or 0), r[6]), reverse=True)
        write_csv("cluster-summary.csv", ["f_id", "n_members", "members", "mean_weighted", "max_weighted", "top10_mentions", "borda"], crow)
        unmapped = sorted(set(features) - set(mapping))
        report += ["", "## Consolidated features (clusters)", ""]
        report += md_table(["F-ID", "Members", "Raw IDs", "Mean weighted", "Max weighted", "Top-10", "Borda"], crow)
        if unmapped:
            report.append(f"\nUnmapped raw features: {', '.join(unmapped)}")

    votes = parse_votes()
    if votes:
        totals: dict[str, int] = defaultdict(int)
        backers: dict[str, list[str]] = defaultdict(list)
        for voter, alloc in votes.items():
            for f_id, pts in alloc.items():
                totals[f_id] += pts
                if pts > 0:
                    backers[f_id].append(f"{voter}:{pts}")
        vrows = sorted(([f, totals[f], len(backers[f]), " ".join(backers[f])] for f in totals), key=lambda r: (r[1], r[2]), reverse=True)
        write_csv("final-ranking.csv", ["f_id", "points", "n_backers", "backers"], vrows)
        report += ["", "## Round 3 — final vote (100 points per agent)", ""]
        report += md_table(["F-ID", "Points", "Backers", "Allocation"], vrows)
        report += [""] + [f"- {v}: allocated {sum(a.values())} points" for v, a in sorted(votes.items())]

    (OUT / "summary.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
