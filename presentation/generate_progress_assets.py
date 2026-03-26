from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/wzm/学习/工作/喷漆/code/repo_zip_download_20260326_0153/extracted/--main")
LOG_DIR = ROOT / "progress_capture"
ASSET_DIR = ROOT / "presentation" / "assets"
ASSET_DIR.mkdir(parents=True, exist_ok=True)

ZH_FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
MONO_FONT = "/System/Library/Fonts/Menlo.ttc"


def load_font(path, size):
    return ImageFont.truetype(path, size)


TITLE_FONT = load_font(ZH_FONT, 28)
SUB_FONT = load_font(ZH_FONT, 18)
BODY_FONT = load_font(ZH_FONT, 22)
SMALL_FONT = load_font(ZH_FONT, 17)
MONO = load_font(MONO_FONT, 18)


def clean_lines(text):
    lines = [line.rstrip() for line in text.splitlines()]
    return [line for line in lines if line.strip()]


def extract_last_display(log_text):
    parts = re.split(r"\x1b\[H\x1b\[2J\x1b\[3J", log_text)
    screens = [part.strip() for part in parts if "智能停车场管理大屏" in part]
    if not screens:
        return "No display output captured."
    return screens[-1]


def tail_lines(path, count=12):
    text = path.read_text(encoding="utf-8", errors="ignore")
    return clean_lines(text)[-count:]


def draw_window(draw, x, y, w, h, title, body_lines, title_color):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=20, fill=(18, 24, 34), outline=(45, 54, 72), width=2)
    draw.rounded_rectangle((x, y, x + w, y + 58), radius=20, fill=title_color)
    draw.rectangle((x, y + 29, x + w, y + 58), fill=title_color)
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = x + 26 + i * 20
        draw.ellipse((cx, y + 18, cx + 12, y + 30), fill=color)
    draw.text((x + 88, y + 14), title, font=SUB_FONT, fill=(255, 255, 255))
    ty = y + 76
    for line in body_lines:
        draw.text((x + 22, ty), line, font=MONO if all(ord(ch) < 128 for ch in line) else SMALL_FONT, fill=(233, 239, 245))
        ty += 28


def create_dashboard_image():
    raw = (LOG_DIR / "display.log").read_text(encoding="utf-8", errors="ignore")
    display_text = extract_last_display(raw)
    lines = clean_lines(display_text)

    img = Image.new("RGB", (1440, 900), (244, 247, 251))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((70, 70, 1370, 830), radius=28, fill=(255, 255, 255), outline=(220, 228, 236), width=2)
    draw.text((110, 115), "Current Dashboard Snapshot", font=TITLE_FONT, fill=(26, 47, 79))
    draw.text(
        (110, 165),
        "This screenshot was generated from the latest runtime output of subscriber_display.py.",
        font=SUB_FONT,
        fill=(82, 94, 111),
    )
    draw_window(draw, 110, 240, 1220, 500, "subscriber_display.py", lines, (42, 127, 144))
    img.save(ASSET_DIR / "demo_dashboard.png")


def create_services_image():
    stats_lines = tail_lines(LOG_DIR / "stats.log", 11)
    gateway_lines = tail_lines(LOG_DIR / "gateway.log", 12)

    img = Image.new("RGB", (1600, 900), (244, 247, 251))
    draw = ImageDraw.Draw(img)
    draw.text((80, 70), "Runtime Services and Decision Flow", font=TITLE_FONT, fill=(26, 47, 79))
    draw.text(
        (80, 120),
        "The statistics service keeps publishing summaries, and the gate controller reacts to new vehicle requests.",
        font=SUB_FONT,
        fill=(82, 94, 111),
    )
    draw_window(draw, 80, 190, 690, 620, "subscriber_stats.py", stats_lines, (31, 91, 168))
    draw_window(draw, 830, 190, 690, 620, "subscriber_gateway.py", gateway_lines, (214, 131, 58))
    img.save(ASSET_DIR / "demo_services.png")


def create_publishers_image():
    sensor_lines = tail_lines(LOG_DIR / "sensor.log", 12)
    vehicle_lines = tail_lines(LOG_DIR / "vehicle.log", 10)

    img = Image.new("RGB", (1600, 900), (244, 247, 251))
    draw = ImageDraw.Draw(img)
    draw.text((80, 70), "Publishers Sending Live MQTT Messages", font=TITLE_FONT, fill=(26, 47, 79))
    draw.text(
        (80, 120),
        "Sensor updates and vehicle entry requests are both active, which proves that the prototype is already event-driven.",
        font=SUB_FONT,
        fill=(82, 94, 111),
    )
    draw_window(draw, 80, 190, 690, 620, "publisher_sensor.py", sensor_lines, (42, 143, 136))
    draw_window(draw, 830, 190, 690, 620, "publisher_vehicle_request.py", vehicle_lines, (187, 92, 44))
    img.save(ASSET_DIR / "demo_publishers.png")


def process_github_shot():
    raw_path = ASSET_DIR / "github_commits.png"
    if not raw_path.exists():
        return
    raw = Image.open(raw_path).convert("RGB")
    left = 50
    top = 120
    right = raw.width - 50
    bottom = min(raw.height - 40, 1160)
    cropped = raw.crop((left, top, right, bottom))

    canvas = Image.new("RGB", (cropped.width + 100, cropped.height + 120), (244, 247, 251))
    draw = ImageDraw.Draw(canvas)
    draw.text((50, 30), "GitHub Commit History", font=TITLE_FONT, fill=(26, 47, 79))
    draw.rounded_rectangle(
        (40, 70, canvas.width - 40, canvas.height - 30),
        radius=24,
        fill=(255, 255, 255),
        outline=(220, 228, 236),
        width=2,
    )
    canvas.paste(cropped, (50, 85))
    canvas.save(ASSET_DIR / "github_commits_framed.png")


if __name__ == "__main__":
    create_dashboard_image()
    create_services_image()
    create_publishers_image()
    process_github_shot()
    print(ASSET_DIR)
