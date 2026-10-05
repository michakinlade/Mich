"""Build KDP interior PDF: 8.5x11in, no bleed, 300 DPI, blank page behind each drawing."""
import glob
from PIL import Image, ImageFilter
import numpy as np

DPI = 300
PAGE_W, PAGE_H = int(8.5 * DPI), int(11 * DPI)  # 2550 x 3300
MARGIN = int(0.5 * DPI)                          # meets KDP 0.375in gutter / 0.25in outside
BOX_W, BOX_H = PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN

def prepare(path):
    im = Image.open(path).convert("L")
    scale = min(BOX_W / im.width, BOX_H / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=80, threshold=2))
    # Levels: pure white paper, solid black lines, keep smooth anti-aliased edges
    a = np.asarray(im).astype(float)
    a = np.clip((a - 60) / (200 - 60) * 255, 0, 255).astype("uint8")
    page = Image.new("L", (PAGE_W, PAGE_H), 255)
    page.paste(Image.fromarray(a), ((PAGE_W - im.width) // 2, (PAGE_H - im.height) // 2))
    return page

files = sorted(glob.glob("[0-2][0-9]-*.*"))
assert len(files) == 20, files
blank = Image.new("L", (PAGE_W, PAGE_H), 255)
pages = []
for f in files:
    pages += [prepare(f), blank]
pages[0].save("interior-8.5x11-no-bleed.pdf", save_all=True, append_images=pages[1:],
              resolution=DPI, quality=95)
print(len(pages), "pages")
