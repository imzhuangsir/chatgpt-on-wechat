from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1080, 1440
BG = "#111318"
FG = "#F3EFE7"
ACCENT = "#C9A66B"
MUTED = "#BEB8AD"
BORDER = "#1D2028"
MARGIN_X = 96
CONTENT_W = WIDTH - 2 * MARGIN_X

SANS_FONT_CANDIDATES = [
    "/workspace/assets/fonts/NotoSansSC-VF.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
]
SERIF_FONT_CANDIDATES = [
    "/workspace/assets/fonts/NotoSerifSC-VF.ttf",
    "/workspace/assets/fonts/NotoSansSC-VF.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
]


def get_font(size: int, serif: bool = False) -> ImageFont.FreeTypeFont:
    candidates = SERIF_FONT_CANDIDATES if serif else SANS_FONT_CANDIDATES
    for path in candidates:
        p = Path(path)
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    wrapped: list[str] = []
    for raw_line in text.split("\n"):
        if not raw_line:
            wrapped.append("")
            continue
        cur = ""
        for ch in raw_line:
            test = cur + ch
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                cur = test
            else:
                if cur:
                    wrapped.append(cur)
                cur = ch
        if cur:
            wrapped.append(cur)
    return wrapped


def draw_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    x: int,
    y_start: int,
    font: ImageFont.FreeTypeFont,
    fill: str,
    gap: int,
) -> int:
    y = y_start
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        h = draw.textbbox((0, 0), line if line else " ", font=font)[3]
        y += h + gap
    return y


def draw_center_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    y_start: int,
    font: ImageFont.FreeTypeFont,
    fill: str,
    gap: int,
) -> int:
    y = y_start
    for line in lines:
        bbox = draw.textbbox((0, 0), line if line else " ", font=font)
        w = bbox[2] - bbox[0]
        x = (WIDTH - w) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += (bbox[3] - bbox[1]) + gap
    return y


def init_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(20, 20), (WIDTH - 20, HEIGHT - 20)], radius=32, outline=BORDER, width=3)
    return img, draw


def make_cover(output_path: Path) -> None:
    img, draw = init_canvas()

    top_font = get_font(44, serif=False)
    main_font = get_font(132, serif=True)
    sub_font = get_font(58, serif=False)
    badge_font = get_font(46, serif=False)

    y = 140
    y = draw_center_lines(draw, ["内容生态观察报告"], y, top_font, ACCENT, 10)
    y += 72
    y = draw_center_lines(draw, ["为什么很多博主", "有流量", "却赚不到钱"], y, main_font, FG, 30)
    y += 46
    y = draw_center_lines(draw, ["—— 流量 ≠ 商业价值 ——"], y, sub_font, MUTED, 10)

    badge = "大勺自媒体观察室 · 2026"
    bbox = draw.textbbox((0, 0), badge, font=badge_font)
    bw = bbox[2] - bbox[0] + 56
    bh = bbox[3] - bbox[1] + 30
    bx = (WIDTH - bw) // 2
    by = HEIGHT - 220
    draw.rectangle([(bx, by), (bx + bw, by + bh)], outline=ACCENT, width=3)
    draw.text((bx + 28, by + 15), badge, font=badge_font, fill=ACCENT)

    img.save(output_path, format="PNG")


def make_slide(output_path: Path, section: str, title: str, hint: str, keyline: str) -> None:
    img, draw = init_canvas()

    section_font = get_font(44, serif=False)
    title_font = get_font(76, serif=True)
    hint_font = get_font(46, serif=False)
    key_font = get_font(68, serif=True)

    y = 92
    draw.text((MARGIN_X, y), section, font=section_font, fill=ACCENT)
    y += 84

    title_lines = wrap_text(draw, title, title_font, CONTENT_W)
    y = draw_lines(draw, title_lines, MARGIN_X, y, title_font, FG, 18)
    y += 18

    hint_lines = wrap_text(draw, hint, hint_font, CONTENT_W - 48)
    block_top = y
    block_bottom = y + (draw.textbbox((0, 0), "中", font=hint_font)[3] + 12) * max(1, len(hint_lines))
    draw.line([(MARGIN_X, block_top + 4), (MARGIN_X, block_bottom - 2)], fill=ACCENT, width=8)
    y = draw_lines(draw, hint_lines, MARGIN_X + 28, y, hint_font, MUTED, 12)

    y += 56
    key_lines = wrap_text(draw, keyline, key_font, CONTENT_W)
    draw_lines(draw, key_lines, MARGIN_X, y, key_font, FG, 16)

    img.save(output_path, format="PNG")


def main() -> None:
    out_dir = Path("output/xiaohongshu_media_value")
    out_dir.mkdir(parents=True, exist_ok=True)

    make_cover(out_dir / "00_cover.png")

    slides = [
        ("P1", "现象", "为什么很多博主有流量却赚不到钱", "很多人默认：有流量就会赚钱", "现实是：两者并不等价"),
        ("P2", "数据失衡", "很多账号数据很好，合作却很少", "点赞高、浏览高、粉丝不少", "高曝光，不等于高变现"),
        ("P3", "底层逻辑", "平台与品牌，是两套系统", "平台看传播效率，品牌看商业确定性", "流量逻辑 ≠ 投放逻辑"),
        ("P4", "品牌视角", "品牌真正关心三件事", "稳定人群、信任关系、消费场景", "缺一项，价值都会打折"),
        ("P5", "流量来源", "情绪热点型流量，通常不稳定", "情绪、热点、娱乐、猎奇可爆发", "但很难沉淀长期购买力"),
        ("P6", "高价值账号", "通常具备三个特征", "清晰人群 + 明确场景 + 长期信任", "这类账号商业价值更稳定"),
        ("P7", "结论", "做内容要分清两件事", "流量是注意力，商业是信任关系", "先有信任，后有持续变现"),
    ]

    for idx, section, title, hint, keyline in slides:
        make_slide(out_dir / f"{idx}.png", section, title, hint, keyline)

    print(f"Done: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
