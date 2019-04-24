import os
from PIL import ImageFont


def get_file(path):
    dir = os.path.dirname(__file__)
    return os.path.join(dir, path)


def get_std_font():
    return ImageFont.load_default()


def get_tiny_font():
    file_path = get_file('assets/4x6.pil')
    fnt = ImageFont.load(file_path)
    return fnt
