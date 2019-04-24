# from . import *
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from . import util
from . import LOG_HELPER


def graphic_schedule(stops, width=32, height=32,
                     colour_background=(0, 0, 0, 255), colour_text=(255, 255, 255),
                     colour_time_default=(77, 148, 255), colour_time_warning=(255, 255, 153),
                     colour_time_critical=(255, 204, 204)):
    now = datetime.now()
    LOG_HELPER.debug("Schedule as of {}".format(now))

    img = Image.new('RGBA', (width, height),  colour_background)
    draw = ImageDraw.Draw(img)

    y_offset = 0
    for stop in stops:
        draw_stop(draw, stop, colour_text, colour_time_default, colour_time_warning, colour_time_critical, y_offset)
        y_offset += 16

        if y_offset > height:
            break

    return img


def draw_stop(draw, stop, c_text, c_t_default, c_t_warn, c_t_crit, y_offset=0):

    # Bus label
    x, y = draw_text(draw, stop.label, 1, y_offset - 1, colour=c_text)

    # Draw route direction arrow
    draw_arrow(draw, stop.dir, x, y_offset - 1, colour=c_text)

    # Next bus time
    num_sched = len(stop.next)

    if num_sched == 0:
        x, y = draw_text(draw, "?", 32, y_offset - 1, align="right", colour=c_text)

    if num_sched >= 1:
        m, c = get_stop_format(stop, stop.next[0], c_t_default, c_t_warn, c_t_crit)
        x, y = draw_text(draw, m, 32, y_offset - 1, align="right", colour=c)

    if num_sched >= 3:
        m, c = get_stop_format(stop, stop.next[2], c_t_default, c_t_warn, c_t_crit)
        x, y = draw_text(draw, m, 32, y_offset + 9,
                         align="right", size="tiny", colour=c)
        x, y = draw_text(draw, ",", x, y_offset + 9,
                         align="right", size="tiny", colour=c)

    if num_sched >= 2:
        if num_sched == 2:
            x = 32
        m, c = get_stop_format(stop, stop.next[1], c_t_default, c_t_warn, c_t_crit)
        x, y = draw_text(draw, m, x, y_offset + 9,
                         align="right", size="tiny", colour=c)


def parse_colour_string(colour_string):
    l = colour_string.split(",")
    return tuple(map(int, l))


def get_stop_format(stop, sched, c_t_default, c_t_warn, c_t_crit):
    now = datetime.now()

    msg = "0"
    delta = (sched - now).seconds / 60

    c = c_t_default
    if delta <= stop.min_time:
        c = c_t_crit
    elif delta <= stop.max_time:
        c = c_t_warn

    if sched > now:
        if delta > 0:
            msg = str(delta)
    else:
        c = c_t_crit
        msg = "0"

    return msg, c


def draw_text(draw, text, x, y, align="left", colour=(255, 255, 255), size="normal"):
    if size == "tiny":
        fnt = util.get_tiny_font()
    else:
        fnt = util.get_std_font()

    w, h = draw.textsize(text, font=fnt)

    actual_x = x
    if align == "right":
        actual_x = x - w

    draw.text((actual_x, y), text, colour, fnt)

    if align == "left":
        actual_x = x + w

    actual_y = y + h

    return actual_x, actual_y


def draw_arrow(draw, dir, x, y, colour):
    if dir == "E":
        pts = [(4, 2), (4, 6), (6, 4)]
    elif dir == "W":
        pts = [(4, 2), (4, 6), (2, 4)]
    elif dir == "N":
        pts = [(2, 4), (6, 4), (4, 2)]
    else:
        pts = [(2, 4), (6, 4), (4, 6)]

    act_pts = list()
    for pt in pts:
        act_pts.append((pt[0] + x - 2, pt[1] + y + 1))

    draw.polygon(act_pts, colour, colour)
