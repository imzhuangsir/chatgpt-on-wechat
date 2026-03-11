from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1080, 1440
BG = "white"
FG = "black"
MARGIN_X = 120

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


TITLE_FONT = get_font(84)
SUBTITLE_FONT = get_font(52)
BODY_FONT = get_font(48)
SMALL_FONT = get_font(36)


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


def make_slide(output_path: Path, title: str, body: str) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    y = 180
    y = draw_multiline_left(draw, title, y, TITLE_FONT, line_spacing=22)
    y += 40
    draw.line([(MARGIN_X, y), (WIDTH - MARGIN_X, y)], fill=FG, width=3)
    y += 48
    draw_multiline_left(draw, body, y, BODY_FONT, line_spacing=18)

    img.save(output_path, format="PNG")


def make_cover(output_path: Path) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    y = 220
    y = draw_multiline_center(
        draw,
        "为什么很多博主有流量\n却赚不到钱",
        y,
        TITLE_FONT,
        line_spacing=28,
    )
    y += 40
    y = draw_multiline_center(draw, "流量 ≠ 商业价值", y, SUBTITLE_FONT, line_spacing=18)

    badge_text = "大勺自媒体观察室"
    badge_bbox = draw.textbbox((0, 0), badge_text, font=SMALL_FONT)
    badge_w = badge_bbox[2] - badge_bbox[0] + 48
    badge_h = badge_bbox[3] - badge_bbox[1] + 30
    badge_x = (WIDTH - badge_w) // 2
    badge_y = HEIGHT - 200
    draw.rectangle(
        [(badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h)],
        outline=FG,
        width=3,
    )
    draw.text((badge_x + 24, badge_y + 14), badge_text, font=SMALL_FONT, fill=FG)

    img.save(output_path, format="PNG")


def main() -> None:
    out_dir = Path("output/xiaohongshu_media_value")
    out_dir.mkdir(parents=True, exist_ok=True)

    make_cover(out_dir / "00_cover.png")

    slides = [
        (
            "P1",
            "为什么很多博主\n有流量\n却赚不到钱",
            "很多人做自媒体都会默认一件事\n\n只要有流量\n就会赚钱\n\n但现实并不是这样",
        ),
        (
            "P2",
            "很多账号的数据\n其实很好",
            "点赞很多\n浏览很多\n粉丝也不少\n\n但商业合作却非常少\n\n很多创作者都会困惑\n为什么有流量\n却赚不到钱",
        ),
        (
            "P3",
            "原因其实很简单",
            "平台给流量的逻辑\n和品牌投放的逻辑\n\n是两套完全不同的系统\n\n平台关注的是\n什么内容容易传播",
        ),
        (
            "P4",
            "品牌真正关心的是",
            "有没有稳定的人群\n有没有信任关系\n有没有明确的消费场景\n\n如果没有这些\n\n流量再高\n商业价值也会很低",
        ),
        (
            "P5",
            "很多账号的流量\n来自什么",
            "情绪\n热点\n娱乐\n猎奇\n\n这些流量虽然很多\n但并不稳定\n\n品牌也很难判断\n这些用户是谁",
        ),
        (
            "P6",
            "真正有商业价值的账号\n通常有三个特点",
            "清晰人群\n明确场景\n长期信任\n\n比如\n厨房\n露营\n旅行\n健身\n\n这些内容的商业价值\n往往更稳定",
        ),
        (
            "P7",
            "最后要记住",
            "流量\n只是注意力\n\n商业\n才是信任\n\n这两件事情\n从来不是一回事",
        ),
    ]

    for idx, title, body in slides:
        make_slide(out_dir / f"{idx}.png", title, body)

    print(f"Done: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
