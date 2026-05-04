#!/usr/bin/env python3
"""Generate cover image for 织女渡 (The Weaver's Ferry)."""

import random
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ── Config ──────────────────────────────────────────────
W, H = 900, 1200
OUTPUT = "/Users/tianxiang/claudecode/writer/cover.png"

# Fonts
XINGKAI = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/13b8ce423f920875b28b551f9406bf1014e0a656.asset/AssetData/Xingkai.ttc"
PINGFANG = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/86ba2c91f017a3749571a82f2c6d890ac7ffb2fb.asset/AssetData/PingFang.ttc"

# Colors
DEEP_BLACK = (8, 6, 10)
SOFT_BLACK = (18, 15, 22)
MUTED_GOLD = (168, 142, 92)
BRIGHT_GOLD = (212, 182, 120)
DARK_CRIMSON = (92, 18, 22)
BURGUNDY = (58, 16, 20)
PALE_GOLD = (198, 178, 138)


# ── Utility ────────────────────────────────────────────
def blend(a, b, t):
    """Linear blend between two colors."""
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ── Fabric texture ─────────────────────────────────────
def make_fabric_texture(w, h):
    """Generate a base fabric-like texture using layered noise."""
    # Use a smaller base and scale up for efficiency + natural feel
    bw, bh = w // 4, h // 4
    base = Image.new("L", (bw, bh))
    px = base.load()
    random.seed(42)

    # Multiple noise layers at different scales
    for y in range(bh):
        for x in range(bw):
            v = 0
            # Large-scale variation
            v += math.sin(x * 0.03) * math.cos(y * 0.04) * 40
            # Medium weave
            v += math.sin(x * 0.15) * math.sin(y * 0.15) * 20
            # Fine thread texture
            v += math.sin(x * 0.5 + y * 0.02) * 10
            v += math.sin(y * 0.5 + x * 0.02) * 10
            # Random grain
            v += random.gauss(0, 12)
            px[x, y] = int(max(0, min(255, 128 + v)))

    base = base.resize((w, h), Image.LANCZOS)
    # Subtle directional blur to suggest thread direction
    base = base.filter(ImageFilter.GaussianBlur(radius=0.7))
    return base


def make_thread_overlay(w, h):
    """Create subtle vertical/horizontal thread lines."""
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    random.seed(77)

    # Vertical threads (warp)
    for x in range(0, w, random.randint(3, 7)):
        alpha = random.randint(3, 15)
        # Slight wobble
        points = [(x + random.gauss(0, 0.8), y) for y in range(0, h, 4)]
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]],
                      fill=(200, 170, 130, alpha), width=1)

    # Horizontal threads (weft) - fewer, more subtle
    for y in range(0, h, random.randint(8, 20)):
        alpha = random.randint(2, 8)
        points = [(x, y + random.gauss(0, 0.5)) for x in range(0, w, 4)]
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]],
                      fill=(180, 150, 110, alpha), width=1)

    return overlay


def make_gradient_background(w, h):
    """Dark atmospheric gradient with subtle color variation."""
    img = Image.new("RGB", (w, h))
    px = img.load()
    random.seed(13)

    for y in range(h):
        t = y / h  # 0 at top, 1 at bottom
        for x in range(w):
            xt = x / w

            # Base: deep black at top, slightly warmer at bottom
            base_color = blend(DEEP_BLACK, (22, 16, 22), t * 0.3)

            # Subtle burgundy glow in center-right
            cx, cy = w * 0.65, h * 0.55
            dist_center = math.sqrt(((x - cx) / w * 2) ** 2 + ((y - cy) / h * 2) ** 2)
            glow = max(0, 1 - dist_center) ** 2 * 0.12
            base_color = blend(base_color, BURGUNDY, glow)

            # Subtle gold accent top-left
            dist_gold = math.sqrt(((x - w * 0.2) / w * 2) ** 2 + ((y - h * 0.25) / h * 2) ** 2)
            gold_glow = max(0, 1 - dist_gold) ** 3 * 0.08
            base_color = blend(base_color, MUTED_GOLD, gold_glow)

            # Micro variation for grain
            noise = random.gauss(0, 2)
            r = max(0, min(255, base_color[0] + noise))
            g = max(0, min(255, base_color[1] + noise))
            b = max(0, min(255, base_color[2] + noise))
            px[x, y] = (int(r), int(g), int(b))

    return img


def make_vignette(w, h):
    """Dark vignette overlay for edges."""
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(vignette)
    cx, cy = w / 2, h / 2
    max_dist = math.sqrt(cx ** 2 + cy ** 2)

    for y in range(0, h, 2):
        for x in range(0, w, 2):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2) / max_dist
            alpha = int(min(180, dist ** 2.5 * 200))
            draw.rectangle([x, y, x + 2, y + 2],
                           fill=(4, 2, 6, alpha))

    return vignette


def make_wood_box_texture(w, h):
    """Subtle camphor wood / antique box texture accents."""
    texture = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    random.seed(99)

    # Suggest wood grain lines in the lower portion
    base_y = int(h * 0.72)
    for row in range(6):
        y = base_y + row * 18
        alpha = 25 - row * 4
        if alpha <= 0:
            break
        points = []
        x = 0
        while x < w:
            points.append((x, y + random.gauss(0, 3)))
            x += random.randint(15, 35)
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]],
                      fill=(140, 110, 70, alpha), width=random.randint(1, 2))

    # Subtle corner ornament suggestion
    corners = [(60, 60), (w - 60, 60), (60, h - 60), (w - 60, h - 60)]
    for cx, cy in corners:
        for r in range(25, 55, 8):
            alpha = 6
            draw.arc([cx - r, cy - r, cx + r, cy + r],
                     0, 90, fill=(180, 150, 110, alpha), width=1)

    return texture


def make_crimson_bleed(w, h):
    """Subtle dark crimson color bleeds suggesting dye/stain."""
    bleed = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    random.seed(55)

    # Create a few organic stain-like shapes
    for _ in range(4):
        cx = random.randint(int(w * 0.1), int(w * 0.9))
        cy = random.randint(int(h * 0.15), int(h * 0.7))
        rx = random.randint(80, 200)
        ry = random.randint(40, 120)
        alpha = random.randint(8, 20)

        # Draw a blurred ellipse
        temp = Image.new("RGBA", (rx * 2, ry * 2), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        temp_draw.ellipse([0, 0, rx * 2, ry * 2],
                          fill=(DARK_CRIMSON[0], DARK_CRIMSON[1], DARK_CRIMSON[2], alpha))
        temp = temp.filter(ImageFilter.GaussianBlur(radius=rx * 0.6))
        bleed.paste(temp, (cx - rx, cy - ry), temp)

    return bleed


def make_hair_threads(w, h):
    """Subtle hair-like threads in the composition."""
    threads = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(threads)
    random.seed(33)

    for _ in range(30):
        # Start points clustered in upper-middle area
        sx = random.randint(int(w * 0.15), int(w * 0.85))
        sy = random.randint(int(h * 0.08), int(h * 0.35))
        length = random.randint(60, 300)
        angle = random.uniform(1.3, 1.85)  # roughly downward
        ex = sx + math.cos(angle) * length
        ey = sy + math.sin(angle) * length

        # Slight curve via control point
        mid_x = (sx + ex) / 2 + random.uniform(-40, 40)
        mid_y = (sy + ey) / 2 + random.uniform(-20, 60)

        alpha = random.randint(4, 18)
        color_choice = random.random()
        if color_choice < 0.5:
            color = (200, 175, 130, alpha)  # gold thread
        else:
            color = (160, 130, 90, alpha)    # muted gold

        # Draw as bezier-like via multiple short segments
        segments = 30
        prev_x, prev_y = sx, sy
        for i in range(1, segments + 1):
            t = i / segments
            # Quadratic bezier
            bx = (1 - t) ** 2 * sx + 2 * (1 - t) * t * mid_x + t ** 2 * ex
            by = (1 - t) ** 2 * sy + 2 * (1 - t) * t * mid_y + t ** 2 * ey
            # Add micro-wobble
            bx += random.gauss(0, 0.3)
            by += random.gauss(0, 0.3)
            if i > 1 or True:
                draw.line([(prev_x, prev_y), (bx, by)],
                          fill=color, width=1)
            prev_x, prev_y = bx, by

    return threads


def add_title(img, w, h):
    """Place the title '织女渡' on the image."""
    # Try Xingkai SC Bold first (calligraphy style), fallback to Kaiti
    try:
        font_title = ImageFont.truetype(XINGKAI, size=120, index=1)  # Bold
    except Exception:
        try:
            font_title = ImageFont.truetype(XINGKAI, size=120, index=0)
        except Exception:
            font_title = ImageFont.truetype(
                "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/88d6cc32a907955efa1d014207889413890573be.asset/AssetData/Kaiti.ttc",
                size=120, index=0)

    # Subtitle / author line
    try:
        font_sub = ImageFont.truetype(PINGFANG, size=28, index=4)  # Light weight
    except Exception:
        font_sub = ImageFont.truetype(PINGFANG, size=28, index=0)

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    title = "织女渡"

    # Title position - centered, slightly above middle
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (w - tw) / 2
    ty = int(h * 0.38)

    # Shadow/glow behind title
    for offset in [(3, 3), (-2, -1), (1, -2), (-3, 2)]:
        draw.text((tx + offset[0], ty + offset[1]), title,
                  font=font_title, fill=(0, 0, 0, 60))

    # Outer glow
    glow_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)
    glow_draw.text((tx, ty), title, font=font_title,
                   fill=(MUTED_GOLD[0], MUTED_GOLD[1], MUTED_GOLD[2], 30))
    glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=8))
    overlay.paste(glow_img, (0, 0), glow_img)

    # Main title in gold
    draw.text((tx, ty), title, font=font_title,
              fill=(BRIGHT_GOLD[0], BRIGHT_GOLD[1], BRIGHT_GOLD[2], 230))

    # Subtle horizontal rule lines
    rule_y1 = ty + th + 30
    rule_y2 = ty - 40
    rule_width = min(tw * 1.3, 400)
    rule_x1 = (w - rule_width) / 2
    rule_x2 = rule_x1 + rule_width

    # Upper rule
    for i in range(3):
        alpha = 40 - i * 10
        y = rule_y2 - i * 4
        draw.line([(rule_x1, y), (rule_x2, y)],
                  fill=(MUTED_GOLD[0], MUTED_GOLD[1], MUTED_GOLD[2], max(0, alpha)),
                  width=1)

    # Lower rule
    for i in range(3):
        alpha = 40 - i * 10
        y = rule_y1 + i * 4
        draw.line([(rule_x1, y), (rule_x2, y)],
                  fill=(MUTED_GOLD[0], MUTED_GOLD[1], MUTED_GOLD[2], max(0, alpha)),
                  width=1)

    # Small ornament dots at rule ends
    for rx in [rule_x1, rule_x2]:
        for ry_offset in [-38, rule_y1 + 10 - ty]:
            ry = ty + ry_offset
            for r in [3, 5]:
                alpha = 30
                draw.ellipse([rx - r, ry - r, rx + r, ry + r],
                             fill=(MUTED_GOLD[0], MUTED_GOLD[1], MUTED_GOLD[2], alpha))

    return overlay


# ── Main ────────────────────────────────────────────────
def main():
    print(f"Generating {W}x{H} cover image...")

    # 1. Gradient background
    bg = make_gradient_background(W, H)

    # 2. Fabric texture on top
    fabric = make_fabric_texture(W, H)
    fabric_rgba = Image.new("RGBA", (W, H))
    for y in range(H):
        for x in range(W):
            v = fabric.getpixel((x, y))
            alpha = int((v - 128) * 0.25)
            alpha = max(0, min(255, alpha))
            fabric_rgba.putpixel((x, y),
                                 (180, 155, 110, alpha))
    bg.paste(fabric_rgba, (0, 0), fabric_rgba)

    # 3. Thread overlay
    threads = make_thread_overlay(W, H)
    bg.paste(threads, (0, 0), threads)

    # 4. Crimson dye bleeds
    crimson = make_crimson_bleed(W, H)
    bg.paste(crimson, (0, 0), crimson)

    # 5. Wood box texture
    wood = make_wood_box_texture(W, H)
    bg.paste(wood, (0, 0), wood)

    # 6. Hair-like threads
    hair = make_hair_threads(W, H)
    bg.paste(hair, (0, 0), hair)

    # 7. Title
    title_overlay = add_title(bg, W, H)
    bg.paste(title_overlay, (0, 0), title_overlay)

    # 8. Vignette (last, on top of everything)
    vignette = make_vignette(W, H)
    bg.paste(vignette, (0, 0), vignette)

    # 9. Save
    bg.save(OUTPUT, "PNG", optimize=True)
    print(f"Saved to {OUTPUT}")


if __name__ == "__main__":
    main()
