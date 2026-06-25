from __future__ import annotations

import argparse
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Markdown reports from rendered 2048 game images."
    )
    parser.add_argument(
        "--games-dir",
        type=Path,
        default=Path("games"),
        help="directory containing game folders such as 001, 002, 003",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("reports"),
        help="directory where Markdown reports will be written",
    )
    return parser.parse_args()


def image_files(game_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in game_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def game_dirs(games_dir: Path) -> list[Path]:
    return sorted(path for path in games_dir.iterdir() if path.is_dir())


def build_report(game_dir: Path, games_dir: Path, reports_dir: Path) -> Path | None:
    images = image_files(game_dir)
    if not images:
        return None

    report_path = reports_dir / f"{game_dir.name}.md"
    lines = [f"# Game {game_dir.name}", ""]

    for image in images:
        relative_image = image.relative_to(reports_dir.parent)
        lines.append(f"![{image.stem}](../{relative_image.as_posix()})")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> None:
    args = parse_args()
    if not args.games_dir.exists():
        raise SystemExit(f"games directory does not exist: {args.games_dir}")

    args.reports_dir.mkdir(parents=True, exist_ok=True)

    created = []
    for game_dir in game_dirs(args.games_dir):
        report = build_report(game_dir, args.games_dir, args.reports_dir)
        if report is not None:
            created.append(report)

    print(f"created reports: {len(created)}")
    for report in created:
        print(report)


if __name__ == "__main__":
    main()
