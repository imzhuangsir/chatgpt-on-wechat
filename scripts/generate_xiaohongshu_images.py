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


def new_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(20, 20), (WIDTH - 20, HEIGHT - 20)], radius=30, outline=STROKE, width=3)
    return img, draw


def make_cover(output_path: Path) -> None:
    img, draw = new_canvas()
    tag_font = load_font("medium", 44)
    title_font = load_font("heavy", 138)
    subtitle_font = load_font("medium", 54)
    brand_font = load_font("regular", 50)

    y = 150
    y = draw_center_text(draw, y, "内容商业观察报告", tag_font, ACCENT)
    y += 88

    for line in ["为什么很多博主", "有流量", "却赚不到钱"]:
        y = draw_center_text(draw, y, line, title_font, FG)
        y += 26

    y += 28
    draw_center_text(draw, y, "流量 ≠ 商业价值", subtitle_font, MUTED)

    brand_text = "大勺自媒体观察室 · 2026"
    draw_center_text(draw, HEIGHT - 200, brand_text, brand_font, ACCENT)

    img.save(output_path, format="PNG")


def make_slide(output_path: Path, section: str, title: str, support: str, keyline: str) -> None:
    img, draw = new_canvas()
    section_font = load_font("medium", 42)
    title_font = load_font("heavy", 80)
    support_font = load_font("regular", 44)
    key_font = load_font("bold", 68)

    y = 92
    draw.text((MARGIN_X, y), section, font=section_font, fill=ACCENT)
    y += 86

    title_lines = wrap_text(draw, title, title_font, CONTENT_WIDTH)
    y = draw_left_lines(draw, MARGIN_X, y, title_lines, title_font, FG, 18)
    y += 20

    support_lines = wrap_text(draw, support, support_font, CONTENT_WIDTH - 50)
    line_height = draw.textbbox((0, 0), "中", font=support_font)[3]
    block_height = max(1, len(support_lines)) * (line_height + 14)
    draw.line([(MARGIN_X, y + 2), (MARGIN_X, y + block_height - 10)], fill=ACCENT, width=8)
    y = draw_left_lines(draw, MARGIN_X + 30, y, support_lines, support_font, MUTED, 14)

    y += 60
    key_lines = wrap_text(draw, keyline, key_font, CONTENT_WIDTH)
    draw_left_lines(draw, MARGIN_X, y, key_lines, key_font, FG, 16)

    img.save(output_path, format="PNG")


def main() -> None:
    out_dir = PROJECT_ROOT / "output/xiaohongshu_media_value"
    out_dir.mkdir(parents=True, exist_ok=True)

    make_cover(out_dir / "00_cover.png")

    pages = [
        ("现象", "为什么很多博主有流量，却赚不到钱", "很多创作者默认：有流量就会赚钱", "现实是：两者并不等价"),
        ("数据失衡", "很多账号数据很好，合作却很少", "点赞高、浏览高、粉丝不少，但商单稀缺", "高曝光，不等于高变现"),
        ("底层逻辑", "平台与品牌，是两套系统", "平台追求传播效率，品牌追求商业确定性", "流量逻辑 ≠ 投放逻辑"),
        ("品牌视角", "品牌真正关心三件事", "稳定人群、信任关系、消费场景", "缺一项，价值都会打折"),
        ("流量来源", "情绪热点型流量，通常不稳定", "情绪、热点、娱乐、猎奇可以爆发", "但难沉淀长期购买力"),
        ("高价值账号", "通常具备三个核心特征", "清晰人群 + 明确场景 + 长期信任", "这类账号商业价值更稳定"),
        ("结论", "做内容要分清两件事", "流量是注意力，商业是信任关系", "先有信任，后有持续变现"),
    ]

    for idx, page in enumerate(pages, start=1):
        section, title, support, keyline = page
        make_slide(out_dir / f"P{idx}.png", section, title, support, keyline)

    print(f"Done: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
