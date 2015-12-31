from base_tests import _BaseDBTest
import json
from biodata import model
import os
import re
from pyquery import PyQuery as pq
import datetime
from werkzeug.datastructures import MultiDict

curdir = os.path.dirname(os.path.abspath(__file__))


class ControllerTest(_BaseDBTest):
    """
    Tests all the controllers by calling them and comparing their output to
    static html files in the html folder.
    """

    def setUp(self):
        _BaseDBTest.setUp(self)
        self.maxDiff = None
        self.whitespace_re = re.compile("^[\s]+", re.MULTILINE)

    def tearDown(self):
        _BaseDBTest.tearDown(self)

    def test_form(self):
        """
        Test form display and operation.
        """

        for base, dirs, files in os.walk(os.path.join(curdir, 'html')):
            for file in files:
                if file != "new.html":
                    continue
                endpt = "%s/new" % base.split(os.path.join(curdir, 'html'))[-1]
                if endpt == "/rvc_species/new":
                    continue
                if endpt == "/rvc_species/observation/new":
                    endpt = "%s?sample=25" % endpt
                print("Fetching %s" % endpt)
                response = self.client.get(endpt)
                self.assertEqual(response.status_code, 200)
                result = response.get_data(as_text=True)
                result = re.sub(self.whitespace_re, "", result)
                # remove whitespace at the beginning of a line
                f = open(os.path.join(base, file), 'r')
                expected = f.read()
                # remove whitespace at the beginning of a line
                expected = re.sub(self.whitespace_re, "", expected)
                self.assertMultiLineEqual(expected, result)

    def test_form_submission_error(self):
        """
        Testing if submitting an empty form results in validation errors.
        """

        data = {}
        response = self.client.post('/rvc_species/observer/new', data=data)
        self.assertEqual(response.status_code, 200)
        d = pq(response.get_data(as_text=True))
        self.assertEqual(len(d(".error")), 2)

    def test_form_submission_redirect(self):
        """
        Add an observer and test if it gets stored. Also check if the result
        is a redirect to the list page.
        """

        data = {'name': 'dolftest'}
        response = self.client.post('/rvc_species/observer/new', data=data,
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            observers = self.session.query(model.rvc_species.Observer).all()
            self.assertEqual(len(observers), 3)

        response = self.client.post('/rvc_species/observer/new', data=data,
                                    follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location,
                         'http://localhost/rvc_species/observer/')

    def test_form_submission_form(self):
        """
        Test if adding redirect=form to the data results in the user being
        shown an empty form again with the redirect value preserved.
        """
        data = {'name': 'dolftest', 'redirect': 'form'}
        response = self.client.post('/rvc_species/observer/new', data=data,
                                    follow_redirects=False)
        self.assertEqual(response.status_code, 200)
        result = response.get_data(as_text=True)
        print(result)
        d = pq(result)
        self.assertEqual(len(d(".error")), 0)
        self.assertEqual(d("input#name").attr.value, '')
        self.assertEqual(d("input#id").attr.value, '')
        self.assertEqual(d("input#redirect").attr.value, 'form')

    def test_form_submission_ajax(self):
        """
        Test form submission from AJAX and value storage.
        Test while using many-to-many and many-to-one relationships
        and date and datetime fields.
        """
        data = [('site', '1'),
                ('participants', '1'),
                ('participants', '2'),
                ('speciesgroup', '1'),
                ('date', '2015-01-01'),
                ]
        data = MultiDict(data)
        headers = [('X_REQUESTED_WITH', '')]
        response = self.client.post('/rvc_species/sample/new', data=data,
                                    headers=headers, follow_redirects=False)
        print(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location,
                         'http://localhost/rvc_species/sample/3')
        with self.app.app_context():
            query = self.session.query(model.rvc_species.Sample)
            samples = query.all()
            self.assertEqual(len(samples), 3)
            sample = query.get(3)
            self.assertEqual(sample.date, datetime.date(2015, 01, 01))
            site = self.session.query(model.rvc_species.Site).get(1)
            self.assertEqual(sample.site, site)
            query = self.session.query(model.rvc_species.Observer)
            participants = [query.get(1), query.get(2)]
            self.assertEqual(sample.participants, participants)

    def test_master_form(self):
        """
        Test the /rvc_species/new form.
        """

        endpt = "/rvc_species/new"
        response = self.client.get(endpt)
        self.assertEqual(response.status_code, 200)
        result = response.get_data(as_text=True)
        result = re.sub(self.whitespace_re, "", result)
        # remove whitespace at the beginning of a line
        base = os.path.join(curdir, 'html', 'rvc_species')
        f = open(os.path.join(base, 'new.html'), 'r')
        expected = f.read()
        # remove whitespace at the beginning of a line
        expected = re.sub(self.whitespace_re, "", expected)
        self.assertMultiLineEqual(expected, result)

    def test_list_json(self):
        """
        Test the list controller while requesting json.
        """
        endpt = "/rvc_species/observer/"
        print("Fetching %s" % endpt)
        headers = {'Accept': 'application/json'}
        response = self.client.get(endpt,
                                   content_type='application/json',
                                   headers=headers)
        self.assertEqual(response.status_code, 200)
        result = response.get_data(as_text=True)
        result = json.loads(result)
        print(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], list)
        self.assertEqual(len(result[0]), 2)
        self.assertIsInstance(result[0][0], int)
        self.assertIsInstance(result[1], list)
        self.assertIsInstance(result[1][0], int)
        self.assertEqual(len(result[1]), 2)

    def test_list_sort(self):
        """
        Test the sort order of the list controller.
        """
        endpt = "/rvc_species/observer/"
        print("Fetching %s" % endpt)
        headers = {'Accept': 'application/json'}
        response = self.client.get(endpt,
                                   content_type='application/json',
                                   headers=headers)
        self.assertEqual(response.status_code, 200)
        result = response.get_data(as_text=True)
        result = json.loads(result)
        print(result)
        self.assertEqual(result[0][1], 'annelies')
        self.assertEqual(result[1][1], 'dolf')
        endpt = "/rvc_species/sample/"
        print("Fetching %s" % endpt)
        headers = {'Accept': 'application/json'}
        response = self.client.get(endpt,
                                   content_type='application/json',
                                   headers=headers)
        self.assertEqual(response.status_code, 200)
        result = response.get_data(as_text=True)
        result = json.loads(result)
        print(result)
        self.assertEqual(result[0][0], 2)

    def test_list(self):
        """
        Test the list controller without selection parameters.
        """

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
                result = re.sub(self.whitespace_re, "", result)
                f = open(os.path.join(base, file), 'r')
                expected = f.read()
                # remove whitespace at the beginning of a line
                expected = re.sub(self.whitespace_re, "", expected)
                self.assertMultiLineEqual(expected, result)

    def test_show(self):
        """
        Test the show controller.
        """

        for base, dirs, files in os.walk(os.path.join(curdir, 'html')):
            for file in files:
                if file != "1.html":
                    continue
                endpt = "%s/1" % base.split(os.path.join(curdir, 'html'))[-1]
                print("Fetching %s" % endpt)
                response = self.client.get(endpt)
                self.assertEqual(response.status_code, 200)
                result = response.get_data(as_text=True)
                result = re.sub(self.whitespace_re, "", result)
                # remove whitespace at the beginning of a line
                f = open(os.path.join(base, file), 'r')
                expected = f.read()
                # remove whitespace at the beginning of a line
                expected = re.sub(self.whitespace_re, "", expected)
                self.assertMultiLineEqual(expected, result)

    def test_delete(self):
        """
        Test the list controller with selection parameters.
        """

        with self.app.app_context():
            samples = self.session.query(model.rvc_species.Sample).all()
            self.assertEqual(len(samples), 2)
            # should return 405 as only GET is allowed.
            response = self.client.post('/rvc_species/sample/delete/1')
            self.assertEqual(response.status_code, 405)
            response = self.client.get('/rvc_species/sample/delete/1')
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
        url = '%s&time="21:38:40.882212"' % url
        response = self.client.get(url)
        d = pq(response.get_data(as_text=True))
        self.assertEqual(len(d(".datarow")), 2)
