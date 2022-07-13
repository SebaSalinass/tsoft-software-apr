import os

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import Color
from config import BASEDIR

## ---------- PATHS
PROJ_DIR = os.path.join(BASEDIR, 'app')
FONT_DIR = os.path.join(PROJ_DIR, 'static/fonts')
IMG_DIR = os.path.join(PROJ_DIR, 'static/img')
LOGO_DIR = os.path.join(IMG_DIR, 'logo.png')

## ---------- SIZES
WIDTH, HEIGHT = LETTER
SZ_SINGLE = (HEIGHT/2, WIDTH)
SZ_MULTIPLE = (HEIGHT, WIDTH)

## ---------- COLORS
COLOR_WHITE = Color(*(255/255, 255/255, 255/255))
COLOR_BLACK = Color(*(0/255, 0/255, 0/255))
COLOR_DRAK_GRAY = Color(*(68/255, 68/255, 68/255))
COLOR_PRIMARY = Color(*(225/255, 70/255, 86/255))
COLOR_PRIMARY_DARK = Color(*(255/255, 255/255, 255/255))
COLOR_DANGER = Color(*(253/255, 203/255, 95/255))

## ---------- FONT SIZES
WATER_HEADER_FONT_SIZE = 10
WATER_SUBHEADER_FONT_SIZE = 8
WATER_TABLE_TITLE_FONT_SIZE = 8.5