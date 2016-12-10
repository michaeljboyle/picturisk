import logging
import json
import webapp2
import re
import svgwrite as svg
import math

PERSON = """
  <g id="svg_3">
   <path id="svg_1" d="m251.030228,136.790359c14.424759,0 26.085861,-11.200279 26.085861,-25.129311c0,-13.842712 -11.661102,-25.10305 -26.085861,-25.10305c-14.335464,0 -25.996552,11.260338 -25.996552,25.10305c0.003906,13.929031 11.665009,25.129311 25.996552,25.129311z" fill="#231F20"/>
   <path id="svg_2" d="m215.83696,380.531555c0,7.799683 6.436951,14.105438 14.514221,14.105438c8.046127,0 14.607452,-6.305756 14.607452,-14.105438l0,-118.203491l12.236404,0l0,118.203491c0,7.799683 6.561279,14.105438 14.607483,14.105438c8.07724,0 14.545288,-6.305756 14.545288,-14.105438l0.089386,-203.800781l12.146973,0l0,75.128967c0,15.130096 20.375854,15.130096 20.375854,0l0,-76.769241c0,-16.684067 -13.453094,-32.989014 -33.677277,-32.989014l-68.994843,-0.086334c-18.494553,0 -33.311905,14.544601 -33.311905,32.60994l0,77.238373c0,14.953705 20.496307,14.953705 20.496307,0l0,-75.13269l12.360794,0l0,203.800781l0.00386,0z" fill="#231F20"/>
  </g>
  """

def get_path_id(path):
  return path.split('/')[-1]

def get_greatest_square(n):
  x = n
  while True:
    y = (x + n / x) / 2
    if (y >= x):
      return x
    x = y

def create_stickman(d, p, x_origin, y_origin, fill):
  scale_fx = p / 130.0
  g = svg.container.Group(transform='translate({} {}) scale({})'.format(x_origin, y_origin, scale_fx))
  r = d.rect(insert=(0, 0), size=(130, 130), fill='white')
  g1 = svg.container.Group()
  c = d.circle(center=(65.5, 15.5), r=9.5, fill=fill)
  str_commands = 'M86,38A11.48,11.48,0,0,0,75,27v0H55v0A11.48,11.48,0,0,0,44,38h0V70a4,4,0,0,0,8,0V45.45L53,46v73h0A5.5,5.5,0,0,0,64,119h0V76h2v43h0A5.5,5.5,0,0,0,77,119h0V46l1-.52V70a4,4,0,0,0,8,0V38Z'
  path = d.path(d=str_commands, fill=fill)
  g1.elements = [c, path]
  g.elements = [r, g1]
  return g

def create_shape(drawing, p, x, y, shape, fill, stroke_w):
  if shape == 'rect':
    return drawing.rect(insert=(x * p, y * p), size=(p, p),
                   fill=fill, stroke='white', stroke_width=stroke_w)
  if shape == 'circle':
    offset = p / 2
    return drawing.circle(center=(x * p + offset, y * p + offset), r = offset,
                   fill=fill, stroke='white', stroke_width=stroke_w)
  if shape == 'person':
    return create_stickman(drawing, p, x * p, y * p, fill)

def create_img(odds, shape='rect', color1='black', color2='red',
               width=100, height=100):
  print odds
  vals = odds.split(':')
  num = int(vals[0])
  total = int(vals[1])
  print total

  min_dim = int(math.floor(get_greatest_square(total)))
  print min_dim

  max_dim = int(math.ceil(total * 1.0 / min_dim))
  print max_dim

  if total >= 100 and num < max_dim:
    return create_large_img(odds, shape, color1, color2, width, height)

  
  p = math.floor(width / max_dim)
  stroke_w = int(math.floor(p / 7))
  
  standout_index = math.floor(total * 0.75)
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
      d.add(create_shape(d, p, x, y, shape, fill_color, stroke_w))
      count += 1
  return d.tostring()


def create_large_img(odds, shape='rect', color1='black', color2='red',
                     width=1000, height=1000):
  print odds
  vals = odds.split(':')
  num = int(vals[0])
  total = int(vals[1])
  print total
  min_dim = int(math.floor(get_greatest_square(total)))
  print min_dim
  max_dim = int(math.ceil(total * 1.0 / min_dim))
  print max_dim
  p = math.floor(width / max_dim)
  stroke_w = int(math.floor(p / 7))
  
  standout_index = math.floor(min_dim * 0.75)
  print standout_index

  d = svg.Drawing(size=(width, height))
  repeat = create_shape(d, p, 0, 0, shape, color1, p / 7)
  pattern = d.pattern(insert=(0, 0), size=(p, p),
                      patternUnits="userSpaceOnUse", id='pattern')
  pattern.add(repeat)

  d.defs.add(pattern)

  d.add(d.rect(insert=(0, 0),
               size=(max_dim * p, p * standout_index),
               fill='url(#pattern)'))

  for i in range(num):
    if shape == 'rect':
      d.add(d.rect(insert=(i * p, p * standout_index),
                   size=(p, p), fill=color2,
                   stroke='white', stroke_width=stroke_w))
    elif shape == 'circle':
      offset = p / 2
      d.add(d.circle(center=(i * p + offset, p * standout_index + offset),
                   r=offset, fill=color2,
                   stroke='white', stroke_width=stroke_w))
    elif shape == 'person':
      d.add(create_stickman(d, p, i * p, p * standout_index, color2))

  
  d.add(d.rect(insert=((i + 1) * p, standout_index * p),
               size=(p * (max_dim - (i + 1)), p),
               fill='url(#pattern)'))

  if (standout_index + 2 < min_dim):
    d.add(d.rect(insert=(0, p * (standout_index + 1)),
                 size=(p * max_dim, p * (min_dim - standout_index - 2)),
                 fill='url(#pattern)'))
  d.add(d.rect(insert=(0, p * (min_dim - 1)),
               size=(p * (total - max_dim * (min_dim - 1)), p),
               fill='url(#pattern)'))
  return d.tostring() 
  

def get_odds_ratio(str_risk):
  odds_re = r'^\d+:\d+$'
  match = re.match(odds_re, str_risk)
  if match:
    return match.group()

  decimal_re = r'^0?\.\d+$'
  match = re.match(decimal_re, str_risk)
  if match:
    total = int(math.floor(1.0 / float(match.group())))
    return '1:' + str(total)

  raise ValueError('The odds did not fit allowed formats (e.g. 1:100 or 0.01)')


class ImageRequestHandler(webapp2.RequestHandler):

  def get(self):
    try:
      odds = get_odds_ratio(self.request.get('odds'))
    except ValueError as e:
      self.response.write(e)
      self.response.set_status(500)
      return

    # Check shape
    shape = 'rect'
    shape_req = self.request.get('shape')
    if shape_req == 'circle':
      shape = 'circle'
    elif shape_req == 'person':
      shape = 'person'

    # Check colors
    color_re = r'^[\dA-Fa-f]{6}$'

    color1 = 'black'
    color1_req = self.request.get('color1')
    print color1_req
    if re.match(color_re, color1_req):
      color1 = '#' + re.match(color_re, color1_req).group()

    print color1

    color2 = 'red'
    color2_req = self.request.get('color2')
    if re.match(color_re, color2_req):
      color2 = '#' + re.match(color_re, color2_req).group()

    # Check dimensions
    w = self.request.get('w')
    h = self.request.get('h')
    num_re = r'^\d+$'
    if re.match(num_re, w) and re.match(num_re, h):
      img = create_img(odds, shape, color1, color2, int(w), int(h))
    else:
      img = create_img(odds, shape, color1, color2)

    self.response.headers['content-type'] = 'image/svg+xml'
    self.response.write(img)
    

app = webapp2.WSGIApplication([
  ('/api/.*', ImageRequestHandler)
], debug=True)