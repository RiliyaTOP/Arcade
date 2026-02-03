from pathlib import Path
from PIL import Image


def slice_row(src_path, out_dir, fw, fh, frames, prefix):
    src_path = Path(src_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(src_path).convert("RGBA")

    for i in range(frames):
        x0 = i * fw
        y0 = 0
        crop = img.crop((x0, y0, x0 + fw, y0 + fh))
        crop.save(out_dir / f"{prefix}_{i}.png")


def main():
    src = Path("resources/Tiny Swords (Free Pack)/Particle FX/Dust_01.png")
    out = Path("resources/_cache_fx/dust01")
    slice_row(src, out, fw=64, fh=64, frames=8, prefix="dust")
    print("OK: resources/_cache_fx/dust01/dust_*.png")


if __name__ == "__main__":
    main()
