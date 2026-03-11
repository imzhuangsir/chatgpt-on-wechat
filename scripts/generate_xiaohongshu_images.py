from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1080, 1440
BG = "#111216"
FG = "#F4F1E8"
ACCENT = "#C8A46A"
MUTED = "#C9C4BA"
MARGIN_X = 92

FONT_PATH_CANDIDATES = [
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
]


def get_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATH_CANDIDATES:
        p = Path(path)
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


COVER_TITLE_FONT = get_font(126)
COVER_SUBTITLE_FONT = get_font(56)
TITLE_FONT = get_font(74)
BODY_FONT = get_font(52)
SMALL_FONT = get_font(34)


def draw_multiline_center(
    draw: ImageDraw.ImageDraw,
    text: str,
    y_start: int,
    font: ImageFont.FreeTypeFont,
    line_spacing: int = 16,
    fill: str = FG,
) -> int:
    y = y_start
    for line in text.split("\n"):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (WIDTH - w) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += (bbox[3] - bbox[1]) + line_spacing
    return y


def draw_multiline_left(
    draw: ImageDraw.ImageDraw,
    text: str,
    y_start: int,
    font: ImageFont.FreeTypeFont,
    line_spacing: int = 14,
    fill: str = FG,
) -> int:
    y = y_start
    for line in text.split("\n"):
        draw.text((MARGIN_X, y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        y += (bbox[3] - bbox[1]) + line_spacing
    return y


def make_slide(output_path: Path, section: str, title: str, body: str, keyline: str) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # Subtle border card to match "report" style.
    draw.rounded_rectangle(
        [(24, 24), (WIDTH - 24, HEIGHT - 24)],
        radius=30,
        outline="#202126",
        width=3,
    )

    y = 92
    draw.text((MARGIN_X, y), section, font=SMALL_FONT, fill=ACCENT)
    y += 82
    y = draw_multiline_left(draw, title, y, TITLE_FONT, line_spacing=20, fill=FG)

    y += 28
    draw.line([(MARGIN_X, y), (MARGIN_X, y + 120)], fill=ACCENT, width=8)
    draw_multiline_left(draw, body, y - 4, SMALL_FONT, line_spacing=16, fill=MUTED)

    key_y = y + 220
    draw_multiline_left(draw, keyline, key_y, BODY_FONT, line_spacing=16, fill=FG)

    img.save(output_path, format="PNG")


def make_cover(output_path: Path) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        [(24, 24), (WIDTH - 24, HEIGHT - 24)],
        radius=30,
        outline="#202126",
        width=3,
    )

    y = 160
    y = draw_multiline_center(
        draw,
        "内容生态观察报告",
        y,
        SMALL_FONT,
        line_spacing=12,
        fill=ACCENT,
    )
    y += 84
    y = draw_multiline_center(
        draw,
        "为什么很多博主\n有流量\n却赚不到钱",
        y,
        COVER_TITLE_FONT,
        line_spacing=30,
    )
    y += 52
    y = draw_multiline_center(
        draw,
        "—— 流量 ≠ 商业价值 ——",
        y,
        COVER_SUBTITLE_FONT,
        line_spacing=18,
        fill=MUTED,
    )

    badge_text = "大勺自媒体观察室 · 2026"
    badge_bbox = draw.textbbox((0, 0), badge_text, font=SMALL_FONT)
    badge_w = badge_bbox[2] - badge_bbox[0] + 48
    badge_h = badge_bbox[3] - badge_bbox[1] + 30
    badge_x = (WIDTH - badge_w) // 2
    badge_y = HEIGHT - 230
    draw.rectangle(
        [(badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h)],
        outline=ACCENT,
        width=3,
    )
    draw.text((badge_x + 24, badge_y + 14), badge_text, font=SMALL_FONT, fill=ACCENT)

    img.save(output_path, format="PNG")


def main() -> None:
    out_dir = Path("output/xiaohongshu_media_value")
    out_dir.mkdir(parents=True, exist_ok=True)

    make_cover(out_dir / "00_cover.png")

    slides = [
        (
            "P1",
            "现象",
            "为什么很多博主\n有流量却赚不到钱",
            "很多人默认\n有流量就会赚钱",
            "现实是：两者并不等价",
        ),
        (
            "P2",
            "数据失衡",
            "很多账号数据很好\n合作却很少",
            "点赞多 浏览多 粉丝不少\n但商单依旧稀缺",
            "高曝光 ≠ 高变现",
        ),
        (
            "P3",
            "底层逻辑",
            "平台与品牌\n是两套系统",
            "平台看传播效率\n品牌看商业确定性",
            "流量逻辑 ≠ 投放逻辑",
        ),
        (
            "P4",
            "品牌视角",
            "品牌真正关心三件事",
            "稳定人群\n信任关系\n消费场景",
            "缺一项，价值都会打折",
        ),
        (
            "P5",
            "流量来源",
            "情绪热点型流量\n通常不稳定",
            "情绪 热点 娱乐 猎奇\n可以爆，但难沉淀",
            "品牌难判断用户会不会买",
        ),
        (
            "P6",
            "高价值账号",
            "通常具备三个特征",
            "清晰人群\n明确场景\n长期信任",
            "厨房/露营/旅行/健身更稳定",
        ),
        (
            "P7",
            "结论",
            "做内容要分清两件事",
            "流量是注意力\n商业是信任关系",
            "先有信任，后有持续变现",
        ),
    ]

    for idx, section, title, body, keyline in slides:
        make_slide(out_dir / f"{idx}.png", section, title, body, keyline)

    print(f"Done: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
