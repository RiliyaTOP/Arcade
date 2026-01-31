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
    base = Path("resources/mainChatacter/without_outline")
    out = Path("resources/mainChatacter/frames")

    fw, fh = 96, 84

    slice_strip(base / "WALK.png", out / "walk", fw, fh, 8, "walk")
    slice_strip(base / "RUN.png", out / "run", fw, fh, 8, "run")
    slice_strip(base / "ATTACK 1.png", out / "attack1", fw, fh, 6, "attack")
    slice_strip(base / "IDLE.png", out / "idle", fw, fh, 6, "idle")


    print("OK: sliced frames into resources/mainChatacter/frames/")


if __name__ == "__main__":
    main()
