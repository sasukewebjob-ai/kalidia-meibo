"""
PWAアイコン生成スクリプト
青背景 + 白文字「K」のアプリアイコンを 192px / 512px で生成する。
Android のマスカブルアイコン規格に合わせて、安全エリア（中央80%）の中に文字を収める。
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).parent
BG_COLOR = '#2563eb'  # index.html の --primary と同じ
FG_COLOR = '#ffffff'
TEXT = 'K'


def find_font(size):
    candidates = [
        'C:/Windows/Fonts/arialbd.ttf',
        'C:/Windows/Fonts/arial.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_icon(size: int, out_path: Path):
    img = Image.new('RGB', (size, size), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # マスカブル対応：文字は中央80%の安全エリアに収める
    safe_size = int(size * 0.55)
    font = find_font(safe_size)

    bbox = draw.textbbox((0, 0), TEXT, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) / 2 - bbox[0]
    y = (size - text_h) / 2 - bbox[1]
    draw.text((x, y), TEXT, fill=FG_COLOR, font=font)

    img.save(out_path, 'PNG', optimize=True)
    print(f'wrote {out_path} ({size}x{size})')


if __name__ == '__main__':
    make_icon(192, ROOT / 'icon-192.png')
    make_icon(512, ROOT / 'icon-512.png')
