#!/usr/bin/env python3
"""
Generate reusable 双色球 candidate numbers from historical draw data.

This is not a real predictor. Lottery draws are random; historical frequencies do
not improve the mathematical odds of winning. The script creates transparent,
repeatable picks using long-term frequency, recent weighted frequency, and simple
balance constraints.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import re
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Iterable


API_URL = "http://jc.zhcw.com/port/client_json.php"
REFERER = "https://www.zhcw.com/kjxx/ssq/"
LOTTERY_ID_SSQ = "1"
PAGE_SIZE = 30
DEFAULT_CACHE_DIR = Path(tempfile.gettempdir()) / "ssq_predict"


def pad(num: int | str) -> str:
    return str(num).zfill(2)


def parse_jsonp(text: str) -> dict:
    text = text.strip()
    match = re.match(r"^[^(]*\((.*)\)\s*;?\s*$", text, flags=re.S)
    if match:
        text = match.group(1)
    return json.loads(text)


def fetch_page(page: int, issue_count: int, timeout: float = 15.0) -> dict:
    query = {
        "transactionType": "10001001",
        "lotteryId": LOTTERY_ID_SSQ,
        "type": "0",
        "pageNum": str(page),
        "pageSize": str(PAGE_SIZE),
        "issueCount": str(issue_count),
        "startIssue": "",
        "endIssue": "",
        "startDate": "",
        "endDate": "",
        "tt": f"{random.random():.12f}",
        "callback": "cb",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(
        url,
        headers={
            "Referer": REFERER,
            "User-Agent": "Mozilla/5.0",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return parse_jsonp(response.read().decode("utf-8"))


def page_number(path: Path) -> int:
    match = re.search(r"ssq-page-(\d+)\.jsonp$", path.name)
    return int(match.group(1)) if match else 0


def load_cached_pages(cache_dir: Path) -> list[dict]:
    pages = []
    for path in sorted(cache_dir.glob("ssq-page-*.jsonp"), key=page_number):
        pages.append(parse_jsonp(path.read_text(encoding="utf-8")))
    return pages


def save_page(cache_dir: Path, page: int, payload: dict) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"ssq-page-{page}.jsonp"
    path.write_text(f"cb({json.dumps(payload, ensure_ascii=False)})", encoding="utf-8")


def fetch_history(issue_count: int, cache_dir: Path | None, refresh: bool) -> list[dict]:
    if cache_dir and not refresh:
        cached = load_cached_pages(cache_dir)
        if cached:
            return normalize_draws(cached)[:issue_count]

    first = fetch_page(1, issue_count)
    pages = [first]
    total_pages = int(first.get("pages") or 1)
    if cache_dir:
        save_page(cache_dir, 1, first)

    for page in range(2, total_pages + 1):
        payload = fetch_page(page, issue_count)
        pages.append(payload)
        if cache_dir:
            save_page(cache_dir, page, payload)
        time.sleep(0.08)

    return normalize_draws(pages)[:issue_count]


def normalize_draws(pages: Iterable[dict]) -> list[dict]:
    by_issue = {}
    for page in pages:
        if page.get("resCode") != "000000":
            continue
        for draw in page.get("data", []):
            issue = str(draw.get("issue", ""))
            red = str(draw.get("frontWinningNum", "")).split()
            blue = str(draw.get("backWinningNum", "")).split()
            if issue and len(red) == 6 and len(blue) == 1:
                by_issue[issue] = draw
    return sorted(by_issue.values(), key=lambda draw: str(draw["issue"]), reverse=True)


def count_numbers(draws: list[dict], field: str, max_num: int) -> list[tuple[str, float]]:
    counts = Counter({pad(num): 0.0 for num in range(1, max_num + 1)})
    for draw in draws:
        counts.update(str(draw[field]).split())
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def weighted_count_numbers(
    draws: list[dict],
    field: str,
    max_num: int,
    half_life: float,
) -> list[tuple[str, float]]:
    counts = Counter({pad(num): 0.0 for num in range(1, max_num + 1)})
    decay = half_life / math.log(2)
    for index, draw in enumerate(draws):
        weight = math.exp(-index / decay)
        for num in str(draw[field]).split():
            counts[num] += weight
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def blended_rank(
    draws: list[dict],
    field: str,
    max_num: int,
    half_life: float,
    long_term_weight: float,
) -> list[tuple[str, float]]:
    long_term = count_numbers(draws, field, max_num)
    recent = weighted_count_numbers(draws, field, max_num, half_life)

    score = Counter()
    for rank, (num, _) in enumerate(long_term):
        score[num] += (max_num - rank) * long_term_weight
    for rank, (num, _) in enumerate(recent):
        score[num] += (max_num - rank) * (1.0 - long_term_weight)

    return sorted(score.items(), key=lambda item: (-item[1], item[0]))


def balanced_red(nums: Iterable[str]) -> bool:
    values = sorted(int(num) for num in nums)
    odd_count = sum(num % 2 for num in values)
    zones = [
        sum(num <= 11 for num in values),
        sum(12 <= num <= 22 for num in values),
        sum(num >= 23 for num in values),
    ]
    total = sum(values)
    consecutive_pairs = sum(
        1 for left, right in zip(values, values[1:]) if right == left + 1
    )
    return (
        len(values) == 6
        and len(set(values)) == 6
        and 2 <= odd_count <= 4
        and all(zone >= 1 for zone in zones)
        and max(zones) <= 3
        and 80 <= total <= 135
        and consecutive_pairs <= 2
    )


def generate_picks(
    draws: list[dict],
    pick_count: int,
    half_life: float,
    long_term_weight: float,
) -> list[tuple[list[str], str]]:
    red_rank = blended_rank(
        draws,
        "frontWinningNum",
        max_num=33,
        half_life=half_life,
        long_term_weight=long_term_weight,
    )
    blue_rank = blended_rank(
        draws,
        "backWinningNum",
        max_num=16,
        half_life=half_life,
        long_term_weight=long_term_weight,
    )

    red_candidates = [num for num, _ in red_rank]
    blue_candidates = [num for num, _ in blue_rank]

    reds: list[list[str]] = []
    templates = [
        [0, 3, 7, 12, 17, 23],
        [1, 4, 8, 13, 19, 25],
        [2, 5, 10, 15, 21, 27],
        [0, 6, 11, 16, 22, 29],
        [3, 7, 14, 18, 24, 31],
        [4, 9, 15, 20, 26, 32],
        [5, 10, 16, 22, 28, 30],
        [6, 11, 17, 23, 29, 32],
    ]
    for template in templates:
        nums = sorted({red_candidates[index] for index in template}, key=int)
        if balanced_red(nums) and nums not in reds:
            reds.append(nums)
        if len(reds) >= pick_count:
            break

    for combo in itertools.combinations(red_candidates[:24], 6):
        nums = sorted(combo, key=int)
        if balanced_red(nums) and nums not in reds:
            reds.append(nums)
        if len(reds) >= pick_count:
            break

    blues = blue_candidates[:pick_count]
    return [(red, blues[index % len(blues)]) for index, red in enumerate(reds[:pick_count])]


def format_rank(rows: list[tuple[str, float]], limit: int, decimals: int = 0) -> str:
    formatted = []
    for num, value in rows[:limit]:
        if decimals:
            formatted.append(f"{num}:{value:.{decimals}f}")
        else:
            formatted.append(f"{num}:{int(value)}")
    return " ".join(formatted)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate 双色球 candidate numbers from official historical data."
    )
    parser.add_argument("--draws", type=int, default=1000, help="number of recent draws to analyze")
    parser.add_argument("--picks", type=int, default=5, help="number of candidate sets to print")
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=DEFAULT_CACHE_DIR,
        help=f"directory for cached ssq-page-*.jsonp files; default: {DEFAULT_CACHE_DIR}",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="fetch fresh data from zhcw instead of using cached pages",
    )
    parser.add_argument(
        "--half-life",
        type=float,
        default=110.0,
        help="recent-weight half-life in draws",
    )
    parser.add_argument(
        "--long-term-weight",
        type=float,
        default=0.55,
        help="blend weight for long-term rank; remainder is recent rank",
    )
    args = parser.parse_args()

    draws = fetch_history(args.draws, args.cache_dir, args.refresh)
    if not draws:
        print("No draw data loaded. Try --refresh with network access.", file=sys.stderr)
        return 1

    latest = draws[0]
    oldest = draws[-1]
    red_top = count_numbers(draws, "frontWinningNum", 33)
    blue_top = count_numbers(draws, "backWinningNum", 16)
    red_recent = weighted_count_numbers(draws, "frontWinningNum", 33, args.half_life)
    blue_recent = weighted_count_numbers(draws, "backWinningNum", 16, args.half_life)
    picks = generate_picks(draws, args.picks, args.half_life, args.long_term_weight)

    print("双色球 historical candidate generator")
    print("Important: this cannot predict a random lottery draw; use it only as a transparent选号 heuristic.")
    print()
    print(f"Draws analyzed: {len(draws)}")
    print(
        "Latest draw: "
        f"{latest['issue']} {latest['openTime']} "
        f"{latest['frontWinningNum']} + {latest['backWinningNum']}"
    )
    print(f"Oldest draw: {oldest['issue']} {oldest['openTime']}")
    print()
    print("Long-term hot red:   ", format_rank(red_top, 12))
    print("Long-term hot blue:  ", format_rank(blue_top, 8))
    print("Recent-weight red:   ", format_rank(red_recent, 12, decimals=1))
    print("Recent-weight blue:  ", format_rank(blue_recent, 8, decimals=1))
    print()
    print("Candidate sets:")
    for index, (red, blue) in enumerate(picks, 1):
        print(f"{index}. 红球：{' '.join(red)}    蓝球：{blue}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
