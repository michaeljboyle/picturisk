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

from google.appengine.ext import ndb
from google.appengine.ext import testbed

import draw
# [END imports]


# [START eater_test]
class DrawTestCase(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

# [END eater_test]

    # [START eater_teardown]
    def tearDown(self):
        self.testbed.deactivate()
    # [END eater_teardown]

    def test_get_dims(self):
        draw.PERSON_H = 30
        draw.PERSON_W = 10
        total = 100
        shape = 'square'
        self.assertEqual((10, 10), draw.get_unit_dims(total, shape))
        total = 200
        shape = 'person_rect'
        self.assertEqual((8, 25), draw.get_unit_dims(total, shape))

    def test_get_standout_index(self):
        # Make sure indexing works properly
        num = 1
        total = 10
        sof = 0.0
        self.assertEqual(0, draw.get_standout_index(num, total, sof))
        total = 10
        sof = 0.9
        self.assertEqual(9, draw.get_standout_index(num, total, sof))
        # Make sure it properly backs off from the end
        num = 7
        total = 10
        sof = 0.9
        self.assertEqual(3, draw.get_standout_index(num, total, sof))


# [START main]
if __name__ == '__main__':
    unittest.main()
# [END main]
