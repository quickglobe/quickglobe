import cairosvg
from PIL import Image
import io

SVG = 'favicon.svg'
BG  = '#f4efe4'

def render(size):
    data = cairosvg.svg2png(url=SVG, output_width=size, output_height=size)
    return Image.open(io.BytesIO(data)).convert('RGBA')

def flatten(img, bg=BG):
    base = Image.new('RGB', img.size, bg)
    base.paste(img, mask=img.split()[3])
    return base

# Favicon PNGs
for size in [16, 32, 48]:
    render(size).save(f'favicon-{size}x{size}.png')
    print(f'favicon-{size}x{size}.png')

# apple-touch-icon: 180x180, corners flattened onto solid bg
flatten(render(180)).save('apple-touch-icon.png')
print('apple-touch-icon.png')

# Android Chrome
for size in [192, 512]:
    render(size).save(f'android-chrome-{size}x{size}.png')
    print(f'android-chrome-{size}x{size}.png')

# favicon.ico: multi-resolution
render(256).save('favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
print('favicon.ico')

print('Done.')
