import logging
import json
import webapp2
import re
import math

import record as Record
import draw as Draw


def get_path_id(path):
    return path.split('/')[-1]


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

    raise ValueError('The odds did not fit allowed formats'
                     ' (e.g. 1:100 or 0.01)')


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
        if shape_req in set(['circle', 'person', 'person_rect']):
            shape = shape_req

        # Check colors
        color_re = r'^[\dA-Fa-f]{6}$'

        color1 = 'black'
        color1_req = self.request.get('color1')
        if re.match(color_re, color1_req):
            color1 = '#' + re.match(color_re, color1_req).group()

        color2 = 'red'
        color2_req = self.request.get('color2')
        if re.match(color_re, color2_req):
            color2 = '#' + re.match(color_re, color2_req).group()

        # Check standout_fraction
        standout_frac = self.request.get('index')
        if standout_frac:
            try:
                standout_frac = float(max(min(float(standout_frac), 0.8), 0.0))
            except:
                standout_frac = 0.75
        else:
            standout_frac = 0.75

        # check flip
        right = self.request.get('right')
        if right == '1':
            right = True
        else:
            right = False

        # Check dimensions
        w = self.request.get('w')
        num_re = r'^\d+$'
        if re.match(num_re, w):
            img = Draw.create_img(odds, shape, color1, color2,
                                  standout_frac, right, int(w), int(w))
        else:
            img = Draw.create_img(odds, shape, color1, color2, standout_frac,
                                  right)

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
