# Copyright 2015 Google Inc
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

# [START imports]
import unittest
import mock
import webapp2
import webtest

from google.appengine.ext import ndb
from google.appengine.ext import testbed

import main
# [END imports]


class AppTest(unittest.TestCase):

    def setUp(self):
        app = webapp2.WSGIApplication([('/api/draw.*',
                                        main.ImageRequestHandler)])
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

    def test_get_path_id(self):
        self.assertEqual('abc', main.get_path_id('123/456/abc'))

    def test_get_odds_ratio(self):
        risk = '1:100'
        self.assertEqual('1:100', main.get_odds_ratio(risk))
        risk = '0.1'
        self.assertEqual('1:10', main.get_odds_ratio(risk))
        risk = '123'
        with self.assertRaises(ValueError):
            main.get_odds_ratio(risk)
        risk = '100:50'
        with self.assertRaises(ValueError):
            main.get_odds_ratio(risk)

    def test_get_standout_fraction(self):
        frac = '0.5'
        self.assertEqual(0.5, main.get_standout_fraction(frac))
        # Test default
        frac = 'abc'
        self.assertEqual(0.0, main.get_standout_fraction(frac))

    def test_get_color(self):
        # Test hex
        color_param = 'ff00dd'
        default = 'black'
        self.assertEqual('#ff00dd', main.get_color(color_param, default))
        # Test default
        color_param = None
        self.assertEqual('black', main.get_color(color_param, default))
        # Test string color
        color_param = 'red'
        self.assertEqual('red', main.get_color(color_param, default))

    def test_get_shape(self):
        # Test arg
        shape_req = 'circle'
        self.assertEqual('circle', main.get_shape(shape_req))
        # test default
        shape_req = None
        self.assertEqual('square', main.get_shape(shape_req))

    def test_get_position(self):
        # Test arg
        pos_req = '1'
        self.assertTrue(main.get_position(pos_req))
        pos_req = '0'
        self.assertFalse(main.get_position(pos_req))
        # test default
        pos_req = 'abc'
        self.assertFalse(main.get_position(pos_req))

    def test_get_filetype(self):
        # Test arg
        req = 'png'
        self.assertEqual('png', main.get_filetype(req))
        # test default
        req = 'abc'
        self.assertEqual('svg', main.get_filetype(req))

    # Test the handler
    @mock.patch('main.get_filetype')
    @mock.patch('main.get_position')
    @mock.patch('main.get_shape')
    @mock.patch('main.get_odds_ratio')
    @mock.patch('draw.create_img')
    @mock.patch('main.get_color')
    @mock.patch('main.get_standout_fraction')
    def test_ImageRequestHandler(self, get_frac, get_color, create_img, get_o,
                                 get_shape, get_pos, get_ft):
        get_ft.return_value = 'svg'
        get_frac.return_value = 0.75
        get_color.return_value = 'orange'
        get_o.return_value = '1:50'
        get_pos.return_value = True
        get_shape.return_value = 'square'
        # Test all params except filetype
        params = {
            'odds': '1:100',
            'shape': 'circle',
            'color1': 'blue',
            'color2': 'green',
            'index': '0.5',
            'right': '1',
            'w': '500',
            'num_wide': '500'
        }
        response = self.testapp.get('/api/draw/', params)
        # Check color2 called ok
        get_color.selfAssertTrue([mock.call('blue', 'black'),
                                 mock.call('green', 'red')],
                                 get_color.call_args_list)
        # Check get_frac called ok
        get_frac.assert_called_with('0.5')
        # Check get_odds_ratio called ok
        get_o.assert_called_with('1:100')
        # Check create_img called ok
        create_img.assert_called_with('1:50', shape='square',
                                      color1='orange', color2='orange',
                                      standout_frac=0.75, right=True,
                                      width=500, num_wide=500)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'image/svg+xml')

        # Test with no width arg
        get_ft.return_value = 'svg'
        params = {
            'odds': '1:100',
            'shape': 'circle',
            'color1': 'blue',
            'color2': 'green',
            'index': '0.5',
            'right': '1',
            'num_wide': 500,
            'type': 'png'
        }
        response = self.testapp.get('/api/draw/', params)
        create_img.assert_called_with('1:50', shape='square',
                                      color1='orange', color2='orange',
                                      standout_frac=0.75, right=True,
                                      num_wide=500)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'image/svg+xml')

        # Test bad odds provided
        get_o.side_effect = ValueError()
        params = {}
        response = self.testapp.get('/api/draw/', params, status=400)
        self.assertEqual(response.status_int, 400)


# [START main]
if __name__ == '__main__':
    unittest.main()
# [END main]
