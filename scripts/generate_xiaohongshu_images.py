from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1080, 1440
BG = "#0E1015"
FG = "#F4F1E8"
ACCENT = "#C7A268"
MUTED = "#B6B0A5"
STROKE = "#1F2430"
MARGIN_X = 94
CONTENT_WIDTH = WIDTH - MARGIN_X * 2
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PAGE_TOP_Y = int(HEIGHT * 0.20)

FONT_FILES = {
    "regular": PROJECT_ROOT / "assets/fonts/SourceHanSansSC-Regular.otf",
    "medium": PROJECT_ROOT / "assets/fonts/SourceHanSansSC-Medium.otf",
    "bold": PROJECT_ROOT / "assets/fonts/SourceHanSansSC-Bold.otf",
    "heavy": PROJECT_ROOT / "assets/fonts/SourceHanSansSC-Heavy.otf",
}
FALLBACK_FILES = [
    Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
    Path("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"),
]


def load_font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [FONT_FILES.get(weight), *FALLBACK_FILES]
    for path in candidates:
        if path and path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for src_line in text.split("\n"):
        if not src_line:
            lines.append("")
            continue
        cur = ""
        for ch in src_line:
            probe = cur + ch
            bbox = draw.textbbox((0, 0), probe, font=font)
            if bbox[2] - bbox[0] <= max_width:
                cur = probe
            else:
                if cur:
                    lines.append(cur)
                cur = ch
        if cur:
            lines.append(cur)
    return lines


def draw_left_lines(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    fill: str,
    line_gap: int,
) -> int:
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line if line else " ", font=font)
        y += (bbox[3] - bbox[1]) + line_gap
    return y


def draw_center_text(draw: ImageDraw.ImageDraw, y: int, text: str, font: ImageFont.FreeTypeFont, fill: str) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (WIDTH - w) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return y + h


def measure_block_height(draw: ImageDraw.ImageDraw, lines: list[str], font: ImageFont.FreeTypeFont, line_gap: int) -> int:
    total = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line if line else " ", font=font)
        total += (bbox[3] - bbox[1]) + line_gap
    return max(0, total - line_gap)


def new_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(20, 20), (WIDTH - 20, HEIGHT - 20)], radius=30, outline=STROKE, width=3)
    return img, draw


def make_cover(output_path: Path) -> None:
    img, draw = new_canvas()
    tag_font = load_font("medium", 44)
    title_font = load_font("heavy", 132)
    subtitle_font = load_font("medium", 54)
    brand_font = load_font("regular", 46)

    tag_lines = ["大勺自媒体观察室"]
    title_lines = ["一个账号怎样才算", "真正具备商业价值"]
    subtitle_lines = ["流量账号 vs 商业账号"]

    block_height = (
        measure_block_height(draw, tag_lines, tag_font, 12)
        + 72
        + measure_block_height(draw, title_lines, title_font, 24)
        + 46
        + measure_block_height(draw, subtitle_lines, subtitle_font, 8)
    )
    y = (HEIGHT - block_height) // 2 + 60

    for line in tag_lines:
        y = draw_center_text(draw, y, line, tag_font, ACCENT)
        y += 12
    y += 60

    for line in title_lines:
        y = draw_center_text(draw, y, line, title_font, FG)
        y += 24

    y += 34
    for line in subtitle_lines:
        y = draw_center_text(draw, y, line, subtitle_font, MUTED)
        y += 8

    brand_text = "内容生态观察 / 2026"
    draw_center_text(draw, HEIGHT - 200, brand_text, brand_font, ACCENT)

    img.save(output_path, format="PNG")


def make_slide(output_path: Path, section: str, title: str, support: str, keyline: str) -> None:
    img, draw = new_canvas()
    section_font = load_font("medium", 40)
    title_font = load_font("heavy", 72)
    support_font = load_font("regular", 40)
    key_font = load_font("bold", 60)

    # Shift all content lower for better balance.
    y = PAGE_TOP_Y
    draw.text((MARGIN_X, y), section, font=section_font, fill=ACCENT)
    y += 80

    title_lines = wrap_text(draw, title, title_font, CONTENT_WIDTH)
    y = draw_left_lines(draw, MARGIN_X, y, title_lines, title_font, FG, 16)
    y += 16

    support_lines = wrap_text(draw, support, support_font, CONTENT_WIDTH - 50)
    line_height = draw.textbbox((0, 0), "中", font=support_font)[3]
    block_height = max(1, len(support_lines)) * (line_height + 12)
    draw.line([(MARGIN_X, y + 2), (MARGIN_X, y + block_height - 10)], fill=ACCENT, width=8)
    y = draw_left_lines(draw, MARGIN_X + 30, y, support_lines, support_font, MUTED, 12)

    y += 50
    key_lines = wrap_text(draw, keyline, key_font, CONTENT_WIDTH)
    draw_left_lines(draw, MARGIN_X, y, key_lines, key_font, FG, 14)

    img.save(output_path, format="PNG")


def main() -> None:
    out_dir = PROJECT_ROOT / "output/xiaohongshu_media_value"
    out_dir.mkdir(parents=True, exist_ok=True)

    make_cover(out_dir / "00_cover.png")

    pages = [
        (
            "问题",
            "一个账号怎样才算真正具备商业价值",
            "很多创作者都会困惑：\n为什么有些账号粉丝不多，却经常有品牌合作？",
            "而有些账号数据很好，却很难接到广告",
        ),
        (
            "误区",
            "商业合作看的\n不只是流量",
            "品牌在选择账号时，更看三个东西：\n人群、内容结构、信任关系",
            "流量只是起点，不是决策终点",
        ),
        (
            "第一",
            "人群是否清晰",
            "品牌更关心：这些用户是谁。\n咖啡、露营、厨房、健身、旅行\n这类内容的人群往往非常明确",
            "人群越清晰，投放越确定",
        ),
        (
            "第二",
            "内容是否稳定",
            "今天做情绪、明天做热点、后天做娱乐。\n内容一直变化，品牌很难判断\n用户到底为什么关注你",
            "稳定内容结构，才有稳定商业预期",
        ),
        (
            "第三",
            "有没有长期信任",
            "很多账号流量来自一条爆款，\n但用户与创作者之间并没有建立关系",
            "真正有商业价值的账号，\n往往都有稳定信任感",
        ),
        (
            "本质",
            "平台更容易给流量\n商业更看重信任",
            "流量可以很快出现，也会很快消失。\n但信任，往往需要时间沉淀",
            "短期看播放，长期看关系",
        ),
        (
            "总结",
            "流量是注意力\n商业是信任",
            "真正有商业价值的账号，\n往往建立在信任之上",
            "下一篇：为什么很多博主粉丝很多\n却依然接不到广告？",
        ),
    ]

    for idx, page in enumerate(pages, start=1):
        section, title, support, keyline = page
        make_slide(out_dir / f"P{idx}.png", section, title, support, keyline)

    print(f"Done: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
