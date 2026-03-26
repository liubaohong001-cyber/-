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


def draw_arrow(draw, start, end, color, width=7):
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    if abs(x2 - x1) >= abs(y2 - y1):
        if x2 >= x1:
            head = [(x2, y2), (x2 - 18, y2 - 10), (x2 - 18, y2 + 10)]
        else:
            head = [(x2, y2), (x2 + 18, y2 - 10), (x2 + 18, y2 + 10)]
    else:
        if y2 >= y1:
            head = [(x2, y2), (x2 - 10, y2 - 18), (x2 + 10, y2 - 18)]
        else:
            head = [(x2, y2), (x2 - 10, y2 + 18), (x2 + 10, y2 + 18)]
    draw.polygon(head, fill=color)


def draw_centered_text(draw, box, text, font, fill):
    x1, y1, x2, y2 = box
    lines = text.split("\n")
    line_heights = []
    widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])
    total_h = sum(line_heights) + (len(lines) - 1) * 6
    cy = y1 + (y2 - y1 - total_h) / 2
    for line, w, h in zip(lines, widths, line_heights):
        cx = x1 + (x2 - x1 - w) / 2
        draw.text((cx, cy), line, font=font, fill=fill)
        cy += h + 6


def create_architecture_image():
    img = Image.new("RGB", (1600, 900), (244, 247, 251))
    draw = ImageDraw.Draw(img)
    draw.text((80, 60), "Current Smart Parking Architecture", font=TITLE_FONT, fill=(26, 47, 79))
    draw.text(
        (80, 110),
        "The diagram below reflects the modules that are already connected in the current MQTT demo.",
        font=SUB_FONT,
        fill=(82, 94, 111),
    )

    sensor_box = (90, 220, 430, 340)
    vehicle_box = (90, 470, 430, 590)
    broker_box = (610, 335, 990, 475)
    display_box = (1170, 130, 1510, 250)
    stats_box = (1170, 335, 1510, 455)
    gate_box = (1170, 555, 1510, 675)

    for box, color in [
        (sensor_box, (42, 143, 136)),
        (vehicle_box, (187, 92, 44)),
        (broker_box, (31, 91, 168)),
        (display_box, (42, 143, 136)),
        (stats_box, (214, 131, 58)),
        (gate_box, (42, 127, 144)),
    ]:
        draw.rounded_rectangle(box, radius=24, fill=color, outline=(255, 255, 255), width=3)

    draw_centered_text(draw, sensor_box, "Parking Sensors\npublisher_sensor.py", BODY_FONT, (255, 255, 255))
    draw_centered_text(draw, vehicle_box, "Vehicle Request Generator\npublisher_vehicle_request.py", BODY_FONT, (255, 255, 255))
    draw_centered_text(draw, broker_box, "MQTT Broker\nbroker.hivemq.com", BODY_FONT, (255, 255, 255))
    draw_centered_text(draw, display_box, "Display Service\nsubscriber_display.py", BODY_FONT, (255, 255, 255))
    draw_centered_text(draw, stats_box, "Statistics Service\nsubscriber_stats.py", BODY_FONT, (255, 255, 255))
    draw_centered_text(draw, gate_box, "Gate Controller\nsubscriber_gateway.py", BODY_FONT, (255, 255, 255))

    draw_arrow(draw, (430, 280), (610, 280), (31, 91, 168))
    draw_arrow(draw, (610, 280), (610, 335), (31, 91, 168))
    draw_arrow(draw, (430, 530), (610, 530), (187, 92, 44))
    draw_arrow(draw, (610, 530), (610, 475), (187, 92, 44))
    draw_arrow(draw, (990, 390), (1170, 190), (42, 143, 136))
    draw_arrow(draw, (990, 405), (1170, 395), (214, 131, 58))
    draw_arrow(draw, (990, 430), (1170, 615), (42, 127, 144))
    draw_arrow(draw, (1340, 455), (1340, 515), (214, 131, 58))
    draw_arrow(draw, (1340, 515), (990, 515), (214, 131, 58))
    draw_arrow(draw, (990, 515), (990, 455), (214, 131, 58))

    label_color = (70, 82, 98)
    draw.text((465, 245), "parking/lot/+/status", font=SMALL_FONT, fill=label_color)
    draw.text((453, 553), "parking/gate/request", font=SMALL_FONT, fill=label_color)
    draw.text((1010, 245), "parking/lot/+/status", font=SMALL_FONT, fill=label_color)
    draw.text((1010, 365), "parking/lot/+/status", font=SMALL_FONT, fill=label_color)
    draw.text((1010, 545), "parking/gate/request", font=SMALL_FONT, fill=label_color)
    draw.text((1040, 500), "parking/stats/summary", font=SMALL_FONT, fill=label_color)

    footer = (
        "The parking sensors and vehicle request generator publish live MQTT messages. The display and statistics services subscribe to slot updates, "
        "while the gate controller uses the latest parking summary to decide whether a new car can enter."
    )
    draw.rounded_rectangle((80, 750, 1520, 840), radius=24, fill=(228, 236, 247), outline=(228, 236, 247))
    draw.text((110, 780), footer, font=SMALL_FONT, fill=(26, 47, 79))

    img.save(ASSET_DIR / "architecture_diagram.png")


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
    create_architecture_image()
    process_github_shot()
    print(ASSET_DIR)
