import logging
import json
import webapp2
import re
import math

import record as Record
import draw


def get_path_id(path):
    return path.split('/')[-1]


def get_odds_ratio(str_risk):
    odds_re = r'^\d+:\d+$'
    match = re.match(odds_re, str_risk)
    if match:
        vals = match.group().split(':')
        if int(vals[0]) > int(vals[1]):
            raise ValueError('Numerator cannot be greater than denomerator')
        return match.group()

    decimal_re = r'^0?\.\d+$'
    match = re.match(decimal_re, str_risk)
    if match:
        total = int(math.floor(1.0 / float(match.group())))
        return '1:' + str(total)

    raise ValueError('The odds did not fit allowed formats'
                     ' (e.g. 1:100 or 0.01)')


def get_standout_fraction(frac):
    # Makes sure standout frac is between 0.0 and 1.0
    try:
        standout_frac = float(max(min(float(frac), 1.0), 0.0))
    except:
        standout_frac = 0.75
    return standout_frac


def get_color(color_param, default):
    # Handle hex colors and string colors
    color_re = r'^[\dA-Fa-f]{6}$'
    if color_param:
        if re.match(color_re, color_param):
            return '#' + re.match(color_re, color_param).group()
        else:
            return color_param
    else:
        return default


def get_shape(shape_req):
    # Correct old argument 'rect' which is now square
    if shape_req is 'rect':
        return 'square'
    default = 'square'
    if shape_req in set(['circle', 'person', 'person_rect', 'square']):
        return shape_req
    else:
        return default


def get_position(pos_req):
    if pos_req == '1':
        return True
    return False


class ImageRequestHandler(webapp2.RequestHandler):

    def get(self):

        try:
            odds = get_odds_ratio(self.request.get('odds'))
        except ValueError as e:
            self.response.set_status(400)
            self.response.write(e)
            return

        # Get shape
        shape = get_shape(self.request.get('shape'))

        # Get colors
        color1 = get_color(self.request.get('color1'), 'black')
        color2 = get_color(self.request.get('color2'), 'red')

        # Get standout_fraction
        standout_frac = self.request.get('index')
        standout_frac = get_standout_fraction(standout_frac)

        # check flip
        right = get_position(self.request.get('right'))

        # Check num_wide
        num_wide = self.request.get('num_wide', None)
        if num_wide:
            num_wide = int(num_wide)

        # Check dimensions
        w = self.request.get('w')
        num_re = r'^\d+$'
        if re.match(num_re, w):
            w = int(w)
            img = draw.create_img(odds, shape=shape, color1=color1,
                                  color2=color2, standout_frac=standout_frac,
                                  right=right, width=w, num_wide=num_wide)
        else:
            img = draw.create_img(odds, shape=shape, color1=color1,
                                  color2=color2, standout_frac=standout_frac,
                                  right=right, num_wide=num_wide)

        self.response.headers['content-type'] = 'image/svg+xml'
        self.response.write(img)


class RestHandler(webapp2.RequestHandler):

    def dispatch(self):
        # time.sleep(1)
        super(RestHandler, self).dispatch()

    def SendJson(self, r):
        self.response.headers['content-type'] = 'text/plain'
        self.response.write(json.dumps(r))


class RecordNoKeyHandler(RestHandler):

    def post(self):
        r = json.loads(self.request.body)
        logging.info(r)
        str_odds = r['odds']
        odds = get_odds_ratio(str_odds)
        num, denom = odds.split(':')
        record = Record.new(r['title'], int(num), int(denom), r['citation'])
        self.SendJson(record.json())

    def get(self):
        records = Record.get_all()
        r = [record.json() for record in records]
        self.SendJson(r)


class RecordKeyHandler(RestHandler):

    def get(self):
        str_key = get_path_id(self.request.path)
        r = Record.get(str_key)
        self.SendJson(r.json())

    # Only modifies votes
    def put(self):
        pass

    def delete(self):
        str_key = get_path_id(self.request.path)
        Record.delete(str_key)


app = webapp2.WSGIApplication([
  ('/api/draw.*', ImageRequestHandler),
  ('/api/records', RecordNoKeyHandler),
  ('/api/records/.*', RecordKeyHandler)
], debug=True)
