"""Reproduce two honest views of four explicitly hypothetical commute scenarios.

Run ``python analysis.py`` from any directory. Default paths are relative to
this file, not the current working directory. No network access is performed.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "commute_scenarios.json"
WARNING = "NOT A UM TRANSPORT STUDY"
INK = "#18323D"
MUTED = "#536873"
TEAL = "#147D80"
GOLD = "#B96A16"
GRID = "#DCE3E5"
PAPER = "#FCFCF8"


def validate_data(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate scenario data without silently coercing invalid inputs."""
    if not isinstance(document, dict):
        raise ValueError("The data document must be an object.")
    if document.get("warning") != WARNING:
        raise ValueError("The hypothetical-data warning must be preserved.")
    if document.get("units") != "door-to-door minutes":
        raise ValueError("Expected units: door-to-door minutes.")
    provenance = document.get("provenance")
    if not isinstance(provenance, str) or not provenance.strip():
        raise ValueError("A non-empty provenance statement is required.")
    rows = document.get("data")
    if not isinstance(rows, list) or not rows:
        raise ValueError("At least one scenario is required.")
    seen = set()
    cleaned = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Each scenario must be an object.")
        mode = row.get("mode")
        if not isinstance(mode, str) or not mode.strip():
            raise ValueError("Each scenario needs a non-empty mode.")
        mode = mode.strip()
        if mode.casefold() in seen:
            raise ValueError(f"Duplicate mode: {mode}")
        seen.add(mode.casefold())
        for field in ("p50", "p90"):
            value = row.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{mode}: {field} must be a finite number.")
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{mode}: {field} must be finite and non-negative.")
        if row["p90"] < row["p50"]:
            raise ValueError(f"{mode}: P90 must be at least P50.")
        cleaned.append({"mode": mode, "p50": row["p50"], "p90": row["p90"]})
    return cleaned


def load_data(path: Path = DATA_FILE) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    return document, validate_data(document)


def build_summary(
    document: dict[str, Any], rows: list[dict[str, Any]]
) -> dict[str, Any]:
    """Derive exact differences only; do not invent statistical inference."""
    summary_rows = [
        {**row, "extra_allowance": row["p90"] - row["p50"]}
        for row in rows
    ]
    summary: dict[str, Any] = {
        "title": document.get("title", "Hypothetical commuting scenarios"),
        "warning": WARNING,
        "data_kind": "hand-assigned hypothetical scenario summaries",
        "provenance": document["provenance"],
        "units": document["units"],
        "number_of_scenarios": len(rows),
        "observed_trip_count": 0,
        "extra_allowance_definition": "P90 minus P50, in minutes",
        "rows": summary_rows,
        "p50_order": [
            r["mode"] for r in sorted(rows, key=lambda r: (r["p50"], r["mode"]))
        ],
        "extra_allowance_order": [
            r["mode"]
            for r in sorted(
                summary_rows, key=lambda r: (-r["extra_allowance"], r["mode"])
            )
        ],
        "limitations": [
            "No trips were observed and no percentiles were estimated.",
            "P90-P50 is not a confidence interval or a standard deviation.",
            "Two assumed quantiles cannot establish the full distribution.",
            "The scenario cannot support real-world transport recommendations."
        ],
    }
    by_mode = {row["mode"]: row for row in rows}
    if "Public bus" in by_mode and "Walking" in by_mode:
        bus, walking = by_mode["Public bus"], by_mode["Walking"]
        summary["public_bus_minus_walking"] = {
            "p50_minutes": bus["p50"] - walking["p50"],
            "p90_minutes": bus["p90"] - walking["p90"],
        }
    return summary


def configure_style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 12,
        "text.color": INK,
        "axes.labelcolor": INK,
        "xtick.color": MUTED,
        "ytick.color": INK,
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "svg.fonttype": "none",
        "svg.hashsalt": "hypothetical-commute-practice09",
    })


def decorate_axes(ax: plt.Axes) -> None:
    ax.set_axisbelow(True)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.tick_params(axis="both", length=0, pad=10)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.xaxis.set_major_locator(MultipleLocator(5))


def header(fig: plt.Figure, number: str, title: str, subtitle: str) -> None:
    fig.text(0.075, 0.94, f"SCENARIO LAB  /  {number}", color=TEAL,
             fontsize=11, weight="bold")
    fig.text(0.075, 0.883, title, fontsize=24, weight="bold")
    fig.text(0.075, 0.835, subtitle, fontsize=12, color=MUTED)


def footer(fig: plt.Figure, detail: str) -> None:
    fig.text(0.075, 0.105, WARNING, fontsize=10, weight="bold", color=GOLD)
    fig.text(0.075, 0.067,
             "Source: hand-assigned hypothetical values from Practice 07; no observed trips.",
             fontsize=9.5, color=MUTED)
    fig.text(0.075, 0.035, detail, fontsize=9.5, color=MUTED)


def save_figure(fig: plt.Figure, stem: Path) -> None:
    fig.savefig(stem.with_suffix(".svg"), metadata={"Date": None})
    fig.savefig(stem.with_suffix(".png"), dpi=180,
                metadata={"Software": "Matplotlib"})
    plt.close(fig)


def plot_time_comparison(rows: list[dict[str, Any]], destination: Path) -> None:
    ordered = sorted(rows, key=lambda row: (row["p50"], row["mode"]))
    fig, ax = plt.subplots(figsize=(12, 7.6))
    fig.subplots_adjust(left=0.21, right=0.93, bottom=0.24, top=0.72)
    header(fig, "01", "A typical time is only one reference point",
           "Compare assumed P50 and P90 values on the same time axis.")
    decorate_axes(ax)
    for index, row in enumerate(ordered):
        ax.plot([row["p50"], row["p90"]], [index, index],
                color="#B7C4C7", linewidth=4, zorder=2, solid_capstyle="round")
        ax.scatter(row["p50"], index, s=145, marker="o", color=TEAL,
                   edgecolors=PAPER, linewidths=1.4, zorder=3)
        ax.scatter(row["p90"], index, s=135, marker="s", color=GOLD,
                   edgecolors=PAPER, linewidths=1.4, zorder=3)
        ax.annotate(f'{row["p50"]:g}', (row["p50"], index),
                    xytext=(0, 15), textcoords="offset points",
                    ha="center", color=TEAL, weight="bold", fontsize=12)
        ax.annotate(f'{row["p90"]:g}', (row["p90"], index),
                    xytext=(0, -25), textcoords="offset points",
                    ha="center", color=GOLD, weight="bold", fontsize=12)
    ax.set_yticks(range(len(ordered)), [row["mode"] for row in ordered])
    ax.set_ylim(len(ordered) - 0.55, -0.55)
    maximum = max(row["p90"] for row in ordered)
    ax.set_xlim(0, max(5, math.ceil(maximum / 5) * 5 + 5))
    ax.set_xlabel("Assumed door-to-door travel time (minutes)", labelpad=14)
    ax.legend(handles=[
        Line2D([0], [0], marker="o", linestyle="none", color=TEAL,
               markersize=9, label="P50: assumed median"),
        Line2D([0], [0], marker="s", linestyle="none", color=GOLD,
               markersize=9, label="P90: assumed 90th percentile")
    ], loc="lower left", bbox_to_anchor=(-0.013, 1.055), frameon=False,
        ncol=2, fontsize=11, columnspacing=2)
    footer(fig, "Lines connect two assumed values; they are not confidence intervals or observed ranges.")
    save_figure(fig, destination)


def plot_extra_allowance(rows: list[dict[str, Any]], destination: Path) -> None:
    ordered = sorted(rows, key=lambda row: (-(row["p90"] - row["p50"]), row["mode"]))
    values = [row["p90"] - row["p50"] for row in ordered]
    fig, ax = plt.subplots(figsize=(12, 7.6))
    fig.subplots_adjust(left=0.21, right=0.91, bottom=0.24, top=0.74)
    header(fig, "02", "The gap between the two reference points",
           "P90 minus P50 isolates extra time; it does not measure total journey time.")
    decorate_axes(ax)
    ax.axvline(0, color=INK, linewidth=1.1)
    for index, (row, value) in enumerate(zip(ordered, values)):
        color = GOLD if row["mode"] == "Public bus" else TEAL
        ax.barh(index, value, height=0.52, color=color, zorder=2)
        ax.annotate(f"{value:g} min", (value, index), xytext=(10, 0),
                    textcoords="offset points", va="center",
                    fontsize=13, weight="bold", color=INK)
    ax.set_yticks(range(len(ordered)), [row["mode"] for row in ordered])
    ax.set_ylim(len(ordered) - 0.4, -0.6)
    ax.set_xlim(0, max(5, math.ceil(max(values) / 5) * 5 + 5))
    ax.set_xlabel("Extra allowance = assumed P90 - assumed P50 (minutes)", labelpad=14)
    footer(fig, "Zero-based bars show exact differences; a smaller gap does not necessarily mean a faster journey.")
    save_figure(fig, destination)


def generate(data_file: Path, output_dir: Path) -> dict[str, Any]:
    document, rows = load_data(data_file)
    summary = build_summary(document, rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    configure_style()
    plot_time_comparison(rows, output_dir / "01_time_comparison")
    plot_extra_allowance(rows, output_dir / "02_extra_allowance")
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_FILE)
    parser.add_argument("--output", type=Path, default=BASE_DIR / "figures")
    args = parser.parse_args()
    summary = generate(args.data, args.output)
    print(f"Validated {summary['number_of_scenarios']} hypothetical scenarios.")
    print("Created two SVGs, two PNGs, and summary.json.")
    print(WARNING)


if __name__ == "__main__":
    main()
