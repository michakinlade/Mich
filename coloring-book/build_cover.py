"""Build KDP paperback wraparound cover: back + spine + front, 8.5x11in trim, 0.125in bleed."""
from PIL import Image
import numpy as np

DPI = 300
PAGES = 40
BLEED, TRIM_W, TRIM_H = 0.125, 8.5, 11.0
SPINE = PAGES * 0.002252  # KDP white paper, inches

W = round((BLEED + TRIM_W + SPINE + TRIM_W + BLEED) * DPI)
H = round((BLEED + TRIM_H + BLEED) * DPI)
back_w = round((BLEED + TRIM_W) * DPI)
spine_x0, spine_x1 = back_w, round((BLEED + TRIM_W + SPINE) * DPI)
front_w = W - spine_x1

def panel(path, pw, outer):
    # Scale so the art nearly fills the panel while text keeps ~0.12in from the trim,
    # then fill the remaining gap by mirroring the art's own edges: vertically into
    # the bleed, horizontally only on the outer edge (the spine side stays clean).
    im = Image.open(path).convert("RGB")
    s = 1.68 * 300 / DPI
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    a = np.asarray(im)
    dx, dy = pw - a.shape[1], H - a.shape[0]
    padx = (dx, 0) if outer == "left" else (0, dx)
    return np.pad(a, ((dy // 2, dy - dy // 2), padx, (0, 0)), mode="reflect")

back = panel("cover-back.webp", back_w, "left")
front = panel("cover-front.webp", front_w, "right")
spine_color = np.concatenate([back[:, -5:], front[:, :5]], axis=1).reshape(-1, 3).mean(0)
spine = np.tile(spine_color.astype("uint8"), (H, spine_x1 - spine_x0, 1))

cover = Image.fromarray(np.concatenate([back, spine, front], axis=1))
assert cover.size == (W, H), cover.size
cover.save("cover-wraparound-kdp.pdf", resolution=DPI, quality=95)

print(f"{W}x{H}px = {W/DPI:.3f} x {H/DPI:.3f} in, spine {SPINE:.4f} in ({spine_x1-spine_x0}px)")
