from __future__ import annotations

from pathlib import Path

from src.bitboard import board_to_matrix


try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover
    Image = None
    ImageDraw = None
    ImageFont = None
    PIL_IMPORT_ERROR = exc
else:
    PIL_IMPORT_ERROR = None


TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (60, 58, 50),
    8192: (45, 43, 38),
    16384: (32, 31, 28),
    32768: (21, 20, 18),
    65536: (12, 12, 11),
}


class GameRenderer:
    def __init__(self, size: int = 720) -> None:
        if PIL_IMPORT_ERROR is not None:
            raise RuntimeError(
                "Pillow is required to render JPG files. Install it with: pip install pillow"
            ) from PIL_IMPORT_ERROR
        self.size = size
        self.margin = 34
        self.header = 104
        self.gap = 14
        self.board_size = self.size - self.margin * 2
        self.tile_size = (self.board_size - self.gap * 5) // 4
        self.font_big = self._font(54)
        self.font_medium = self._font(32)
        self.font_small = self._font(24)

    def render_snapshots(
        self,
        history: list[int],
        output_dir: Path,
        count: int,
        final_score: int,
        max_tile: int,
    ) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        indices = self._snapshot_indices(len(history), count)
        for image_number, history_index in enumerate(indices, start=1):
            board = history[history_index]
            self.render_board(
                board=board,
                output_path=output_dir / f"{image_number:03d}.jpg",
                move=history_index,
                final_score=final_score,
                max_tile=max_tile,
            )

    def render_history(
        self,
        history: list[int],
        output_dir: Path,
        final_score: int,
        max_tile: int,
    ) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        for image_number, board in enumerate(history, start=1):
            self.render_board(
                board=board,
                output_path=output_dir / f"{image_number:03d}.jpg",
                move=image_number - 1,
                final_score=final_score,
                max_tile=max_tile,
            )

    def render_board(
        self,
        board: int,
        output_path: Path,
        move: int,
        final_score: int,
        max_tile: int,
    ) -> None:
        image = Image.new("RGB", (self.size, self.size + self.header), (250, 248, 239))
        draw = ImageDraw.Draw(image)

        draw.text((self.margin, 26), "2048 Expectimax", fill=(90, 78, 66), font=self.font_medium)
        summary = f"move {move}  score {final_score}  max {max_tile}"
        draw.text((self.margin, 68), summary, fill=(122, 110, 98), font=self.font_small)

        board_top = self.header
        draw.rounded_rectangle(
            (self.margin, board_top, self.margin + self.board_size, board_top + self.board_size),
            radius=18,
            fill=(187, 173, 160),
        )

        matrix = board_to_matrix(board)
        for row in range(4):
            for col in range(4):
                value = matrix[row][col]
                x0 = self.margin + self.gap + col * (self.tile_size + self.gap)
                y0 = board_top + self.gap + row * (self.tile_size + self.gap)
                x1 = x0 + self.tile_size
                y1 = y0 + self.tile_size
                self._draw_tile(draw, value, x0, y0, x1, y1)

        image.save(output_path, "JPEG", quality=92)

    def _draw_tile(self, draw: ImageDraw.ImageDraw, value: int, x0: int, y0: int, x1: int, y1: int) -> None:
        color = TILE_COLORS.get(value, TILE_COLORS[65536])
        draw.rounded_rectangle((x0, y0, x1, y1), radius=9, fill=color)

        if value == 0:
            return

        text = str(value)
        font = self._tile_font(value)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        fill = (249, 246, 242) if value >= 8 else (119, 110, 101)
        draw.text(
            ((x0 + x1 - text_width) / 2, (y0 + y1 - text_height) / 2 - 4),
            text,
            fill=fill,
            font=font,
        )

    def _tile_font(self, value: int):
        if value < 100:
            return self._font_big_cached
        if value < 1000:
            return self._font(48)
        if value < 10000:
            return self._font(39)
        return self._font(31)

    @property
    def _font_big_cached(self):
        return self.font_big

    @staticmethod
    def _font(size: int):
        for name in ("Arial Bold.ttf", "Arial.ttf", "DejaVuSans-Bold.ttf"):
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    @staticmethod
    def _snapshot_indices(length: int, count: int) -> list[int]:
        if length <= 1:
            return [0] * count
        if count == 1:
            return [length - 1]
        return sorted({round(index * (length - 1) / (count - 1)) for index in range(count)})
