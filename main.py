from __future__ import annotations

import argparse
from pathlib import Path

from src.ai import ExpectimaxAI
from src.bitboard import MAX_TILE
from src.game import Game2048
from src.render import GameRenderer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a 2048 Expectimax AI with a 64-bit bitboard engine."
    )
    parser.add_argument(
        "--games",
        type=int,
        default=1,
        help="number of games to simulate",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="base random seed; each game adds its index to this value",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=6,
        help="maximum expectimax search depth",
    )
    parser.add_argument(
        "--time-limit",
        type=float,
        default=0.08,
        help="soft time limit in seconds per AI move",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("games"),
        help="directory for rendered game snapshots",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="only print the final summary",
    )
    return parser.parse_args()


def run_one_game(
    game_number: int,
    args: argparse.Namespace,
    ai: ExpectimaxAI,
    renderer: GameRenderer,
) -> dict[str, int | bool]:
    seed = None if args.seed is None else args.seed + game_number - 1
    game = Game2048(seed=seed)
    history = [game.board]

    while not game.is_over:
        move = ai.choose_move(game.board)
        if move is None:
            break
        moved = game.move(move)
        if not moved:
            break
        history.append(game.board)

    game_dir = args.output / f"{game_number:03d}"
    renderer.render_history(
        history=history,
        output_dir=game_dir,
        final_score=game.score,
        max_tile=game.max_tile,
    )

    result = {
        "game": game_number,
        "score": game.score,
        "max_tile": game.max_tile,
        "moves": game.moves,
        "reached_limit": game.max_tile >= MAX_TILE,
    }
    if not args.quiet:
        print(
            f"game {game_number:03d}: score={game.score}, "
            f"max={game.max_tile}, moves={game.moves}, "
            f"limit={'yes' if result['reached_limit'] else 'no'}"
        )
    return result


def main() -> None:
    args = parse_args()
    if args.games < 1:
        raise SystemExit("--games must be at least 1")

    args.output.mkdir(parents=True, exist_ok=True)
    ai = ExpectimaxAI(max_depth=args.depth, time_limit=args.time_limit)
    renderer = GameRenderer()

    results = [
        run_one_game(game_number, args, ai, renderer)
        for game_number in range(1, args.games + 1)
    ]

    limit_hits = sum(1 for result in results if result["reached_limit"])
    best_tile = max(int(result["max_tile"]) for result in results)
    avg_score = sum(int(result["score"]) for result in results) / len(results)

    print()
    print(f"games: {len(results)}")
    print(f"{MAX_TILE} limit hits: {limit_hits}/{len(results)} ({limit_hits / len(results):.1%})")
    print(f"best tile: {best_tile}")
    print(f"average score: {avg_score:.0f}")
    print(f"move images: {args.output.resolve()}")


if __name__ == "__main__":
    main()
