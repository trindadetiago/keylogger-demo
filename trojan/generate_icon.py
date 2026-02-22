"""Gera o icone do app Flappy Bird (.icns para macOS) no estilo macOS."""

from PIL import Image, ImageDraw, ImageFilter
import os
import subprocess
import tempfile
import math


def superellipse_points(cx, cy, rx, ry, n=5, num_points=200):
    """Gera pontos de uma superelipse (squircle do macOS usa n~5)."""
    points = []
    for i in range(num_points):
        t = 2 * math.pi * i / num_points
        cos_t = math.cos(t)
        sin_t = math.sin(t)
        x = cx + abs(cos_t) ** (2 / n) * rx * (1 if cos_t >= 0 else -1)
        y = cy + abs(sin_t) ** (2 / n) * ry * (1 if sin_t >= 0 else -1)
        points.append((x, y))
    return points


def create_squircle_mask(size, padding=40):
    """Cria mascara squircle estilo macOS."""
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    r = size // 2 - padding
    points = superellipse_points(size // 2, size // 2, r, r, n=5)
    draw.polygon(points, fill=255)
    return mask


def create_flappy_icon(size=1024):
    """Cria um icone estilo Flappy Bird com formato macOS."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    padding = size * 0.04
    s = size  # alias

    # --- Squircle background (ceu) ---
    mask = create_squircle_mask(s, padding=int(padding))

    bg = Image.new("RGBA", (s, s), (78, 192, 202, 255))
    bg.putalpha(mask)

    # --- Chao ---
    ground = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ground_draw = ImageDraw.Draw(ground)
    ground_y = int(s * 0.75)
    ground_draw.rectangle([0, ground_y, s, s], fill=(222, 216, 149, 255))
    ground_draw.rectangle([0, ground_y, s, ground_y + int(s * 0.03)], fill=(84, 185, 72, 255))
    # Textura do chao
    for x in range(0, s, int(s * 0.04)):
        ground_draw.rectangle(
            [x, ground_y + int(s * 0.035), x + int(s * 0.02), ground_y + int(s * 0.04)],
            fill=(200, 192, 112, 255),
        )
    ground.putalpha(mask)

    img = Image.alpha_composite(img, bg)
    img = Image.alpha_composite(img, ground)

    draw = ImageDraw.Draw(img)

    # --- Nuvens ---
    for cx, cy, sc in [(s * 0.2, s * 0.15, 1.0), (s * 0.72, s * 0.22, 0.7), (s * 0.5, s * 0.08, 0.5)]:
        cr = int(s * 0.055 * sc)
        draw.ellipse([cx - cr * 2, cy - cr * 0.7, cx + cr * 2, cy + cr * 0.7],
                      fill=(255, 255, 255, 140))
        draw.ellipse([cx - cr, cy - cr * 1.4, cx + cr * 1.2, cy - cr * 0.1],
                      fill=(255, 255, 255, 140))

    draw = ImageDraw.Draw(img)

    # --- Canos ---
    pipe_x = int(s * 0.62)
    pipe_w = int(s * 0.1)
    cap_extra = int(s * 0.015)
    cap_h = int(s * 0.035)
    gap_top = int(s * 0.32)
    gap_bot = int(s * 0.52)

    pipe_col = (115, 191, 46, 255)
    pipe_hi = (143, 212, 74, 255)
    pipe_sh = (90, 154, 32, 255)

    # Cano superior
    draw.rectangle([pipe_x, 0, pipe_x + pipe_w, gap_top], fill=pipe_col)
    draw.rectangle([pipe_x, 0, pipe_x + int(pipe_w * 0.3), gap_top], fill=pipe_hi)
    draw.rectangle([pipe_x - cap_extra, gap_top - cap_h,
                     pipe_x + pipe_w + cap_extra, gap_top], fill=pipe_sh)
    draw.rectangle([pipe_x - cap_extra + 2, gap_top - cap_h + 2,
                     pipe_x + pipe_w + cap_extra - 2, gap_top - 2], fill=pipe_col)

    # Cano inferior
    draw.rectangle([pipe_x, gap_bot, pipe_x + pipe_w, ground_y], fill=pipe_col)
    draw.rectangle([pipe_x, gap_bot, pipe_x + int(pipe_w * 0.3), ground_y], fill=pipe_hi)
    draw.rectangle([pipe_x - cap_extra, gap_bot,
                     pipe_x + pipe_w + cap_extra, gap_bot + cap_h], fill=pipe_sh)
    draw.rectangle([pipe_x - cap_extra + 2, gap_bot + 2,
                     pipe_x + pipe_w + cap_extra - 2, gap_bot + cap_h - 2], fill=pipe_col)

    # --- Passaro ---
    bird_cx = int(s * 0.35)
    bird_cy = int(s * 0.42)
    bird_rx = int(s * 0.1)
    bird_ry = int(s * 0.075)

    # Sombra do passaro
    shadow = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([bird_cx - bird_rx + 4, bird_cy - bird_ry + 6,
                bird_cx + bird_rx + 4, bird_cy + bird_ry + 6],
               fill=(0, 0, 0, 40))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)

    # Corpo
    draw.ellipse([bird_cx - bird_rx, bird_cy - bird_ry,
                  bird_cx + bird_rx, bird_cy + bird_ry],
                 fill=(248, 198, 48, 255), outline=(232, 160, 32, 255), width=3)

    # Barriga (highlight)
    belly_rx = int(bird_rx * 0.6)
    belly_ry = int(bird_ry * 0.5)
    draw.ellipse([bird_cx - belly_rx - int(s * 0.01), bird_cy,
                  bird_cx + belly_rx - int(s * 0.01), bird_cy + bird_ry - 2],
                 fill=(252, 220, 100, 255))

    # Asa
    wing_cx = bird_cx - int(bird_rx * 0.2)
    wing_cy = bird_cy + int(bird_ry * 0.15)
    wing_rx = int(bird_rx * 0.5)
    wing_ry = int(bird_ry * 0.55)
    draw.ellipse([wing_cx - wing_rx, wing_cy - wing_ry,
                  wing_cx + wing_rx, wing_cy + wing_ry],
                 fill=(232, 160, 32, 255))

    # Olho branco
    eye_cx = bird_cx + int(bird_rx * 0.4)
    eye_cy = bird_cy - int(bird_ry * 0.25)
    eye_rx = int(bird_rx * 0.28)
    eye_ry = int(bird_ry * 0.4)
    draw.ellipse([eye_cx - eye_rx, eye_cy - eye_ry,
                  eye_cx + eye_rx, eye_cy + eye_ry],
                 fill=(255, 255, 255, 255))

    # Pupila
    pup_cx = eye_cx + int(eye_rx * 0.25)
    pup_cy = eye_cy + int(eye_ry * 0.1)
    pup_r = int(eye_rx * 0.55)
    draw.ellipse([pup_cx - pup_r, pup_cy - int(pup_r * 1.2),
                  pup_cx + pup_r, pup_cy + int(pup_r * 1.2)],
                 fill=(30, 30, 30, 255))

    # Reflexo no olho
    ref_cx = pup_cx - int(pup_r * 0.3)
    ref_cy = pup_cy - int(pup_r * 0.4)
    ref_r = int(pup_r * 0.3)
    draw.ellipse([ref_cx - ref_r, ref_cy - ref_r, ref_cx + ref_r, ref_cy + ref_r],
                 fill=(255, 255, 255, 200))

    # Bico
    beak_x = bird_cx + int(bird_rx * 0.75)
    beak_y = bird_cy + int(bird_ry * 0.1)
    beak_w = int(bird_rx * 0.6)
    beak_h = int(bird_ry * 0.3)
    # Bico superior
    draw.polygon([
        (beak_x, beak_y - beak_h),
        (beak_x + beak_w, beak_y),
        (beak_x, beak_y),
    ], fill=(232, 68, 48, 255))
    # Bico inferior
    draw.polygon([
        (beak_x, beak_y),
        (beak_x + beak_w - int(beak_w * 0.15), beak_y),
        (beak_x, beak_y + beak_h),
    ], fill=(200, 50, 40, 255))

    # --- Aplicar mascara squircle final ---
    final_mask = create_squircle_mask(s, padding=int(padding))
    img.putalpha(final_mask)

    # --- Sombra exterior (drop shadow) ---
    result = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    shadow_mask = final_mask.copy()
    shadow_base = Image.new("RGBA", (s, s), (0, 0, 0, 60))
    shadow_base.putalpha(shadow_mask)
    shadow_offset = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    shadow_offset.paste(shadow_base, (0, int(s * 0.01)))
    shadow_offset = shadow_offset.filter(ImageFilter.GaussianBlur(int(s * 0.02)))
    result = Image.alpha_composite(result, shadow_offset)
    result = Image.alpha_composite(result, img)

    return result


def ImageChops_min(a, b):
    """Min de dois canais (evita import extra)."""
    return Image.fromarray(
        __import__("numpy").minimum(
            __import__("numpy").array(a),
            __import__("numpy").array(b),
        )
    )


def save_as_icns(img, output_path):
    """Converte PIL Image para .icns usando iconutil do macOS."""
    with tempfile.TemporaryDirectory() as tmpdir:
        iconset_dir = os.path.join(tmpdir, "icon.iconset")
        os.makedirs(iconset_dir)

        sizes = [16, 32, 64, 128, 256, 512]
        for s in sizes:
            resized = img.resize((s, s), Image.LANCZOS)
            resized.save(os.path.join(iconset_dir, f"icon_{s}x{s}.png"))
            if s <= 256:
                resized2x = img.resize((s * 2, s * 2), Image.LANCZOS)
                resized2x.save(os.path.join(iconset_dir, f"icon_{s}x{s}@2x.png"))

        subprocess.run(
            ["iconutil", "-c", "icns", iconset_dir, "-o", output_path],
            check=True,
        )


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output = os.path.join(script_dir, "FlappyBird.icns")

    img = create_flappy_icon(1024)
    save_as_icns(img, output)
    img.save(os.path.join(script_dir, "FlappyBird.png"))

    print(f"[+] Icone gerado: {output}")
