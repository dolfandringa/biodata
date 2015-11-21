from base_tests import _BaseDBTest, _BaseTest
import testmodel
import biodata
from biodata import model
import os
import re
import lxml
from pyquery import PyQuery as pq
import json

curdir = os.path.dirname(os.path.abspath(__file__))


class ControllerTest(_BaseDBTest):
    """
    Tests all the controllers by calling them and comparing their output to
    static html files in the html folder.
    """

    def setUp(self):
        _BaseDBTest.setUp(self)
        uri = self.app.config['SQLALCHEMY_DATABASE_URI']
        self.maxDiff = None

    def tearDown(self):
        _BaseDBTest.tearDown(self)

    def test_form(self):
        """
        Test form display and operation.
        """

        self.fail("Test form display.")
        self.fail("Test form submission with validation failures.")
        self.fail("Test form user submission with destination is form. " +
                  "User should be redirected to the form but all fields " +
                  "should be emptied.")
        self.fail("Test form ajax submission with destination is form. " +
                  "User should be redirected to form with hidden " +
                  "and select fields filled in but other fields empty.")
        self.fail("Test user form submission with destination is list. " +
                  "User should be redirected to the list page.")

    def test_list(self):
        """
        Test the list controller without selection parameters.
        """

        r = re.compile("^[\s]+", re.MULTILINE)
        for base, dirs, files in os.walk(os.path.join(curdir, 'html')):
            for file in files:
                if file != "index.html":
                    continue
                endpt = "%s/" % base.split(os.path.join(curdir, 'html'))[-1]
                print("Fetching %s" % endpt)
                response = self.client.get(endpt)
                self.assertEqual(response.status_code, 200)
                result = response.get_data(as_text=True)
                # remove whitespace at the beginning of a line
                result = re.sub(r, "", result)
                f = open(os.path.join(base, file), 'r')
                expected = f.read()
                # remove whitespace at the beginning of a line
                expected = re.sub(r, "", expected)
                self.assertMultiLineEqual(expected, result)

    def test_show(self):
        """
        Test the show controller.
        """

        r = re.compile("^[\s]+", re.MULTILINE)
        for base, dirs, files in os.walk(os.path.join(curdir, 'html')):
            for file in files:
                if file != "1.html":
                    continue
                endpt = "%s/1" % base.split(os.path.join(curdir, 'html'))[-1]
                print("Fetching %s" % endpt)
                response = self.client.get(endpt)
                self.assertEqual(response.status_code, 200)
                result = response.get_data(as_text=True)
                result = re.sub(r, "", result)
                # remove whitespace at the beginning of a line
                f = open(os.path.join(base, file), 'r')
                expected = f.read()
                # remove whitespace at the beginning of a line
                expected = re.sub(r, "", expected)
                self.assertMultiLineEqual(expected, result)

    def test_delete(self):
        """
        Test the list controller with selection parameters.
        """

        with self.app.app_context():
            samples = self.session.query(model.rvc_species.Sample).all()
            self.assertEqual(len(samples), 2)
            response = self.client.get('/rvc_species/sample/delete/1')
            # should return 405 as only POST is allowed.
            self.assertEqual(response.status_code, 405)
            response = self.client.post('/rvc_species/sample/delete/1')
            self.assertEqual(response.status_code, 200)
            result = json.loads(response.get_data())
            self.assertEqual(result, {'success': True})
            samples = self.session.query(model.rvc_species.Sample).all()
            self.assertEqual(len(samples), 1)

    def test_list_arguments(self):
        """
        Test the list controller with selection parameters.
        """

        # both test samples have the same date
        response = self.client.get('/rvc_species/sample/?date="2015-11-18"')
        self.assertEqual(response.status_code, 200)
        d = pq(response.get_data(as_text=True))
        self.assertEqual(len(d(".datarow")), 2)

        # two values for different fields should result in them being AND-ed
        url = '/rvc_species/sample/?date="2015-11-18"&time="21:38:39.881432"'
        response = self.client.get(url)
        d = pq(response.get_data(as_text=True))
        self.assertEqual(len(d(".datarow")), 1)

        # two values for one field should result in them being OR-ed
        url = '/rvc_species/sample/?date="2015-11-18"&time="21:38:39.881432"'
        url = '%s&time="21:38:39.882212"' % url
        response = self.client.get(url)
        d = pq(response.get_data(as_text=True))
        self.assertEqual(len(d(".datarow")), 2)
