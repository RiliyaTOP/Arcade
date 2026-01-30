from pathlib import Path
from PIL import Image


def slice_strip(src_path, out_dir, frame_w, frame_h, frames, prefix):
    src_path = Path(src_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(src_path).convert("RGBA")

    for i in range(frames):
        x0 = i * frame_w
        y0 = 0
        crop = img.crop((x0, y0, x0 + frame_w, y0 + frame_h))
        crop.save(out_dir / f"{prefix}_{i}.png")


def main():
    src = Path("resources/Tiny Swords (Free Pack)/Particle FX/Dust_01.png")
    out = Path("resources/fx/death_puff")

    slice_strip(src, out, 64, 64, 8, "puff")

    print("OK: sliced into resources/fx/death_puff/")


if __name__ == "__main__":
    main()
