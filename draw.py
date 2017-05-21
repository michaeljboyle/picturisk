import svgwrite as svg
import math
import logging

PERSON_W = 50.0
PERSON_H = 130.0
PERSON_SVG_RE = ('M46,38A11.48,11.48,0,0,0,35,27v0H15v0A11.48,11.48,0,0,0,4,'
                 '38H4V70a4,4,0,0,0,8,0V45.45L13,46v73h0A5.5,5.5,0,0,0,24,'
                 '119h0V76h2v43h0A5.5,5.5,0,0,0,37,119h0V46l1-.52V70a4,4,'
                 '0,0,0,8,0V38Z')
PERSON_SVG_SQ = ('M86,38A11.48,11.48,0,0,0,75,27v0H55v0A11.48,11.48,0,0,0,44,'
                 '38h0V70a4,4,0,0,0,8,0V45.45L53,46v73h0A5.5,5.5,0,0,0,64,'
                 '119h0V76h2v43h0A5.5,5.5,0,0,0,77,119h0V46l1-.52V70a4,4,0,'
                 '0,0,8,0V38Z')


def get_greatest_square(n):
    x = n
    while True:
        y = (x + n / x) / 2
        if (y >= x):
            return x
        x = y


def get_unit_dims(total, shape):
    if shape != 'person_rect':
        min_dim = int(math.floor(get_greatest_square(total)))
        max_dim = int(math.ceil(total * 1.0 / min_dim))
    else:
        min_dim = 1
        max_dim = total
        while min_dim * PERSON_H <= max_dim * PERSON_W:
            min_dim += 1
            max_dim = int(math.ceil(total / float(min_dim)))
        min_dim -= 1
        if min_dim < 1:
            min_dim = 1
        max_dim = int(math.ceil(total / float(min_dim)))
    return (min_dim, max_dim)


def get_standout_index(num, total, standout_frac):
    logging.info('standout_frac: %s' % standout_frac)
    max_so_index = total - num
    logging.info('max_so_index: %s' % max_so_index)
    standout_index = int(min(math.floor(total * standout_frac),
                         max_so_index))
    logging.info('standout index: %s' % standout_index)
    return standout_index


def create_stickman(d, p, x_origin, y_origin, fill):
    scale_fx = p / PERSON_H
    g = svg.container.Group(transform='translate({} {}) scale({})'.format(
        x_origin, y_origin, scale_fx))
    r = d.rect(insert=(0, 0), size=(PERSON_H, PERSON_H), fill='white')
    g1 = svg.container.Group()
    c = d.circle(center=(65.5, 15.5), r=9.5, fill=fill)
    path = d.path(d=PERSON_SVG_SQ, fill=fill)
    g1.elements = [c, path]
    g.elements = [r, g1]
    return g


def create_rect_stickman(d, p, x_origin, y_origin, fill):
    scale_fx = p / PERSON_W
    g = svg.container.Group(transform='translate({} {}) scale({})'.format(
        x_origin, y_origin, scale_fx))
    r = d.rect(insert=(0, 0), size=(PERSON_W, PERSON_H), fill='white')
    g1 = svg.container.Group()
    c = d.circle(center=(25.5, 15.5), r=9.5, fill=fill)
    path = d.path(d=PERSON_SVG_RE, fill=fill)
    g1.elements = [c, path]
    g.elements = [r, g1]
    return g


def create_shape(drawing, p, x, y, shape, fill):
    stroke_w = int(math.floor(p / 7))
    if shape == 'square':
        return drawing.rect(insert=(x, y), size=(p, p),
                            fill=fill, stroke='white', stroke_width=stroke_w)
    if shape == 'circle':
        offset = p / 2
        return drawing.circle(center=(x + offset, y + offset), r=offset,
                              fill=fill, stroke='white', stroke_width=stroke_w)
    if shape == 'person':
        return create_stickman(drawing, p, x, y, fill)
    if shape == 'person_rect':
        return create_rect_stickman(drawing, p, x, y, fill)


def create_img(odds, shape='square', color1='black', color2='red',
               standout_frac=0.75, right=False, width=1000, height=None,
               num_wide=None):

    if height is None:
        height = width

    vals = odds.split(':')
    num = int(vals[0])
    total = int(vals[1])

    if num_wide:
        max_dim = num_wide
        min_dim = int(math.ceil(1.0 * total / num_wide))
    else:
        min_dim, max_dim = get_unit_dims(total, shape)

    if 1.0 * width / max_dim < 1.0:
        width = max_dim * 1.0

    logging.info('odds: %s' % odds)
    logging.info('total: %s' % total)
    logging.info('greatest square: %s' % get_greatest_square(total))
    logging.info('min dim: %s' % min_dim)
    logging.info('max dim: %s' % max_dim)

    p = math.floor(width / max_dim)
    logging.info('unit width: %s' % p)
    py = p
    # Change scale for rectangular people
    if shape == 'person_rect':
        py = p * PERSON_H / PERSON_W
    logging.info('unit height: %s' % py)
    height = py * min_dim
    logging.info('height: %s' % height)

    drawing = draw_fig(num, total, min_dim, max_dim, p, py, shape,
                       color1, color2, standout_frac, right, width,
                       height)

    return drawing.tostring()


def draw_fig(num, total, min_dim, max_dim, p, py, shape,
             color1, color2, standout_frac, right, width, height):
    standout_index = get_standout_index(num, total, standout_frac)

    d = svg.Drawing(size=(width, height))

    bg_repeat = create_shape(d, p, 0, 0, shape, color1)
    bg_pattern = d.pattern(insert=(0, 0), size=(p, py),
                           patternUnits="userSpaceOnUse", id='bg_pattern')
    bg_pattern.add(bg_repeat)
    d.defs.add(bg_pattern)

    so_repeat = create_shape(d, p, 0, 0, shape, color2)
    so_pattern = d.pattern(insert=(0, 0), size=(p, py),
                           patternUnits="userSpaceOnUse", id='so_pattern')
    so_pattern.add(so_repeat)
    d.defs.add(so_pattern)

    # Add pattern for everything up to the start of the standout row
    # Start by finding the row in which standout will start
    pre_so_row = int(standout_index) / max_dim
    logging.info('pre_so_row: %s' % pre_so_row)
    so_start_row_left_num_bg = max(standout_index % max_dim, 0)
    logging.info('so_start_row_left_num_bg: %s' % so_start_row_left_num_bg)
    # Check if the first row of standouts will take up entire row
    if (standout_index + num) < ((pre_so_row + 1) * max_dim):
        so_start_row_width = num
        so_start_row_right_num_bg = (
            max_dim - so_start_row_left_num_bg -
            so_start_row_width)
    else:
        so_start_row_width = max_dim - so_start_row_left_num_bg
        so_start_row_right_num_bg = 0
    logging.info('so_start_row_width: %s' % so_start_row_width)
    num_full_so_rows = (num - so_start_row_width) / max_dim
    logging.info('num_full_so_rows: %s' % num_full_so_rows)
    so_last_row_width = (num - so_start_row_width) % max_dim
    rem_bg_total = total - (num + pre_so_row * max_dim +
                            so_start_row_left_num_bg +
                            so_start_row_right_num_bg)
    so_last_row_right_num_bg = min(max_dim - so_last_row_width,
                                   rem_bg_total)

    # First add everything up to standout row
    d.add(d.rect(insert=(0, 0),
                 size=(max_dim * p, py * pre_so_row),
                 fill='url(#bg_pattern)'))
    # Then add bg units at beginning of row
    d.add(d.rect(insert=(0, py * (pre_so_row)),
                 size=(so_start_row_left_num_bg * p, py),
                 fill='url(#bg_pattern)'))
    # Then add so units in that row
    d.add(d.rect(insert=((so_start_row_left_num_bg) * p,
                         py * (pre_so_row)),
                 size=(so_start_row_width * p, py),
                 fill='url(#so_pattern)'))
    # Then add bg units in that row if any
    d.add(d.rect(insert=((so_start_row_left_num_bg + so_start_row_width) * p,
                         py * (pre_so_row)),
                 size=(so_start_row_right_num_bg * p, py),
                 fill='url(#bg_pattern)'))
    # Then add more full standout rows if any
    d.add(d.rect(insert=(0, py * (pre_so_row + 1)),
                 size=(max_dim * p, py * num_full_so_rows),
                 fill='url(#so_pattern)'))
    # Then add partial row of remaining standouts
    d.add(d.rect(insert=(0, py * (pre_so_row + 1 + num_full_so_rows)),
                 size=(so_last_row_width * p, py),
                 fill='url(#so_pattern)'))
    # Then add remainder of this row of bg
    d.add(d.rect(insert=(so_last_row_width * p,
                         py * (pre_so_row + 1 + num_full_so_rows)),
                 size=(so_last_row_right_num_bg * p, py),
                 fill='url(#bg_pattern)'))

    remainder_start_row = pre_so_row + 1 + num_full_so_rows + 1
    rem_bg_full_rows = (rem_bg_total - so_last_row_right_num_bg) / max_dim
    logging.info('rem_bg_full_rows: %s' % rem_bg_full_rows)
    # Then add remaining full rows of bg if any
    d.add(d.rect(insert=(0, py * remainder_start_row),
                 size=(max_dim * p, py * rem_bg_full_rows),
                 fill='url(#bg_pattern)'))

    rem_bg = (rem_bg_total - so_last_row_right_num_bg) % max_dim
    # Then add remainder of last row of bg
    d.add(d.rect(insert=(0, py * (remainder_start_row + rem_bg_full_rows)),
                 size=(rem_bg * p, py),
                 fill='url(#bg_pattern)'))

    return d
