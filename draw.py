import re
import svgwrite as svg
import math

PERSON_W = 50.0
PERSON_H = 130.0

def get_greatest_square(n):
  x = n
  while True:
    y = (x + n / x) / 2
    if (y >= x):
      return x
    x = y

def create_stickman(d, p, x_origin, y_origin, fill):
  scale_fx = p / PERSON_H
  g = svg.container.Group(transform='translate({} {}) scale({})'.format(x_origin, y_origin, scale_fx))
  r = d.rect(insert=(0, 0), size=(PERSON_H, PERSON_H), fill='white')
  g1 = svg.container.Group()
  c = d.circle(center=(65.5, 15.5), r=9.5, fill=fill)
  str_commands = 'M86,38A11.48,11.48,0,0,0,75,27v0H55v0A11.48,11.48,0,0,0,44,38h0V70a4,4,0,0,0,8,0V45.45L53,46v73h0A5.5,5.5,0,0,0,64,119h0V76h2v43h0A5.5,5.5,0,0,0,77,119h0V46l1-.52V70a4,4,0,0,0,8,0V38Z'
  path = d.path(d=str_commands, fill=fill)
  g1.elements = [c, path]
  g.elements = [r, g1]
  return g

def create_rect_stickman(d, p, x_origin, y_origin, fill):
  scale_fx = p / PERSON_W
  g = svg.container.Group(transform='translate({} {}) scale({})'.format(x_origin, y_origin, scale_fx))
  r = d.rect(insert=(0, 0), size=(PERSON_W, PERSON_H), fill='white')
  g1 = svg.container.Group()
  c = d.circle(center=(25.5, 15.5), r=9.5, fill=fill)
  str_commands = 'M46,38A11.48,11.48,0,0,0,35,27v0H15v0A11.48,11.48,0,0,0,4,38H4V70a4,4,0,0,0,8,0V45.45L13,46v73h0A5.5,5.5,0,0,0,24,119h0V76h2v43h0A5.5,5.5,0,0,0,37,119h0V46l1-.52V70a4,4,0,0,0,8,0V38Z'
  path = d.path(d=str_commands, fill=fill)
  g1.elements = [c, path]
  g.elements = [r, g1]
  return g

def create_shape(drawing, p, x, y, shape, fill):
  stroke_w = int(math.floor(p / 7))
  if shape == 'rect':
    return drawing.rect(insert=(x, y), size=(p, p),
                   fill=fill, stroke='white', stroke_width=stroke_w)
  if shape == 'circle':
    offset = p / 2
    return drawing.circle(center=(x + offset, y + offset), r = offset,
                   fill=fill, stroke='white', stroke_width=stroke_w)
  if shape == 'person':
    return create_stickman(drawing, p, x, y, fill)
  if shape == 'person_rect':
    return create_rect_stickman(drawing, p, x, y, fill)

def create_img(odds, shape='rect', color1='black', color2='red',
               standout_frac=0.75, right=False, width=1000, height=1000):
  
  vals = odds.split(':')
  num = int(vals[0])
  total = int(vals[1])
  if total > 100000:
    width = 2000
    height = 2000

  # if the shape is a rect person, it can hold more people in the width,
  # so the max dim needs to go up and min dim needs to go down
  if shape != 'person_rect':
    min_dim = int(math.floor(get_greatest_square(total)))
    max_dim = int(math.ceil(total * 1.0 / min_dim))
  else:
    min_dim = int(math.floor(get_greatest_square(total) * (1 - PERSON_W / PERSON_H)))
    if min_dim < 1:
      min_dim = 1
    max_dim = int(math.ceil(total * 1.0 / min_dim))

  print odds
  print total
  print get_greatest_square(total)
  print min_dim
  print max_dim
  
  p = math.floor(width / max_dim)
  print p
  py = p
  # Change scale for rectangular people
  if shape == 'person_rect':
    py = p * PERSON_H / PERSON_W

  if total >= 100 and num < max_dim:
    return create_large_img(num, total, min_dim, max_dim, p, py, shape,
                            color1, color2, standout_frac, right, width, height)
  else:
    return create_small_img(num, total, min_dim, max_dim, p, py, shape,
                            color1, color2, standout_frac, right, width, height)


def create_small_img(num, total, min_dim, max_dim, p, py, shape,
                     color1, color2, standout_frac, right, width, height):
  
  standout_index = math.floor(total * standout_frac)
  # Adjust standout index to make sure img shows all standouts
  while standout_index + num > total:
    standout_index -= 1
  print standout_index

  d = svg.Drawing(size=(width, height))

  count = 1
  standouts_placed = 0
  for y in range(min_dim):
    for x in range(max_dim):
      if count > total:
        break
      fill_color = color1
      if count >= standout_index and standouts_placed < num:
        fill_color = color2
        standouts_placed += 1
      d.add(create_shape(d, p, x * p, y * py, shape, fill_color))
      count += 1
  return d.tostring()


def create_large_img(num, total, min_dim, max_dim, p, py, shape,
                     color1, color2, standout_frac, right, width, height):
  
  standout_index = math.floor(min_dim * standout_frac)
  print standout_index

  d = svg.Drawing(size=(width, height))

  repeat = create_shape(d, p, 0, 0, shape, color1)
  pattern = d.pattern(insert=(0, 0), size=(p, py),
                      patternUnits="userSpaceOnUse", id='pattern')
  pattern.add(repeat)

  d.defs.add(pattern)

  d.add(d.rect(insert=(0, 0),
               size=(max_dim * p, py * standout_index),
               fill='url(#pattern)'))

  group = svg.container.Group()
  if right:
    group.update({'transform': 'scale(-1, 1) translate(-{}, 0)'.format(max_dim * p)})
  for i in range(num):
    group.elements.append(create_shape(d, p, i * p, standout_index * py, 
                                       shape, color2))

  
  group.elements.append(d.rect(insert=((i + 1) * p, standout_index * py),
                               size=(p * (max_dim - (i + 1)), py),
                               fill='url(#pattern)'))

  d.add(group)

  if (standout_index + 2 < min_dim):
    d.add(d.rect(insert=(0, py * (standout_index + 1)),
                 size=(p * max_dim, py * (min_dim - standout_index - 2)),
                 fill='url(#pattern)'))
  d.add(d.rect(insert=(0, py * (min_dim - 1)),
               size=(p * (total - max_dim * (min_dim - 1)), py),
               fill='url(#pattern)'))
  return d.tostring() 
  