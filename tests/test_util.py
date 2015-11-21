from base_tests import _BaseDBTest, _BaseTest
import datetime
import biodata
from biodata import model
from biodata.util import *
from wtforms import ValidationError, Form, StringField
from wtforms.validators import InputRequired
import tempfile
import os
from testmodel import TestSample, TestObservation, TestParticipant
import types
from collections import OrderedDict


def isint(v):
    try:
        int(v)
        return True
    except TypeError:
        return False


class UtilTest(_BaseTest):
    """
    These unittests test utility functions in biodata.util that are not
    dependent on having an active database connection. Functions that solely
    depend on the SQLAlchemy schema don't need an active connection. Only
    functions that actively select or write rows to the database need one.
    """

    def test_validator(self):
        """
        Test if wrapping a function with the validator function makes it
        fail form validation with incorrect input.
        """

        v = validator("Please enter an integer value", isint)

        class TestForm(Form):
            test = StringField('test', [v])

        class TestForm2(Form):
            test = StringField('test', [v, InputRequired()])

        form = TestForm(data={'test': 1})
        self.assertTrue(form.validate())
        form = TestForm()
        self.assertTrue(form.validate())
        form = TestForm2()
        self.assertFalse(form.validate())
        form = TestForm(data={'test': 'bla'})
        self.assertFalse(form.validate())

    def test_map_column_type(self):
        """
        Tests the mapping of column types.
        """

        inputRequired = wtforms.validators.InputRequired
        type = map_column_type(TestSample.id)
        self.assertEqual(type['label'], 'id')
        self.assertEqual(type['widget'], wtforms.IntegerField)
        self.assertEqual(type['html_attributes'], {})
        type = map_column_type(TestSample.date)
        self.assertEqual(type['label'], 'date')
        self.assertEqual(type['widget'], wtforms.DateField)
        self.assertEqual(type['kwargs']['format'], '%Y-%m-%d')
        self.assertEqual(type['html_attributes'], {})
        self.assertIsInstance(type['args'][0], inputRequired)
        type = map_column_type(TestSample.time)
        self.assertEqual(type['label'], 'time')
        self.assertEqual(type['widget'], wtforms.DateTimeField)
        self.assertEqual(type['kwargs']['format'], '%H:%M')
        self.assertEqual(type['html_attributes'], {})
        type = map_column_type(TestSample.name)
        self.assertEqual(type['label'], 'name')
        self.assertEqual(type['widget'], wtforms.StringField)
        self.assertEqual(type['html_attributes'], {})
        self.assertIsInstance(type['args'][0], inputRequired)

    def test_get_object(self):
        """
        Test if the biodata.util.get_object function
        returns a correct class based on the name of the dataset and object.
        """
        obj = get_object('rvc_species', 'sample')
        self.assertEquals(obj, model.rvc_species.Sample)

    def test_get_simple_columns(self):
        """Test getting the simple columns of an SQLAlchemy object"""

        cols = list(get_simple_columns(TestSample))
        self.assertEqual(len(cols), 3)
        expected = set([u'date', u'time', u'name'])
        self.assertEqual(set([c.key for c in cols]), expected)

    def test_get_relation_attributes(self):
        """
        Test getting one-to-many relation attributes for an SQLAlchemy Object
        """

        cols = list(get_relation_attributes(TestObservation))
        self.assertEqual(len(cols), 1)
        self.assertEqual([c.key for c in cols], [u'sample'])
        cols = list(get_relation_attributes(TestSample))
        self.assertEqual(len(cols), 0)

    def test_get_multi_relation_attributes(self):
        cols = list(get_multi_relation_attributes(TestSample))
        self.assertEqual(len(cols), 1)
        self.assertEqual([c.key for c in cols], [u'participants'])

    def test_get_data_attributes(self):
        """
        Test fetching of sqlalchemy attributes from an SQLAlchemy class
        """
        # Do the attributes with relations first, as the referred objects won't
        # have the backref attribute until the relation is loaded.
        attrs = get_data_attributes(TestObservation)
        self.assertIsInstance(attrs, types.GeneratorType)
        attrs = list(attrs)
        self.assertEqual(len(attrs), 4)
        properties = set(['id', 'name', 'sample_id', 'sample'])
        self.assertEqual(set([a.key for a in attrs]), properties)
        attrs = get_data_attributes(TestParticipant)
        attrs = list(attrs)
        self.assertEqual(len(attrs), 3)
        properties = set(['testsamples', 'id', 'name'])
        self.assertEqual(set([a.key for a in attrs]), properties)
        attrs = get_data_attributes(TestSample)
        attrs = list(attrs)
        self.assertEqual(len(attrs), 6)
        properties = set(['id', 'date', 'time', 'name',
                          'observations', 'participants'])
        self.assertEqual(set([a.key for a in attrs]), properties)


class UtilTestDB(_BaseDBTest):
    """
    This testcase test the utility functions in biodata.util that need to read
    or write rows to/from the database and thus need an active connection.
    """

    def test_get_simple_columns(self):
        """
        Test if the get_simple_columns also works with a real dataset.
        """

        with self.app.app_context():
            cols = list(get_simple_columns(model.rvc_species.Sample))
            self.assertEqual(len(cols), 2)
            expected = set([u'date', u'time'])
            self.assertEqual(set([c.key for c in cols]), expected)

    def test_get_values(self):
        """
        Test the biodata.util.get_values() which fetches the values for an
        SQLAlchemy instance.
        """

        with self.app.app_context():
            sample = self.session.query(model.rvc_species.Sample).get(1)
            values = get_values(sample)
            self.assertEqual(len(values), 6)
            site = self.session.query(model.rvc_species.Site).get(1)
            values = get_values(site)
            self.assertEqual(values['lon'], "")

    def test_get_fields(self):
        """
        The mother of them all. Test if biodata.util.get_fields results in the
        correct loading of the wtforms fields for each SQLAlchemy column.
        """

        with self.app.app_context():
            with self.app.test_request_context('/'):
                fields = get_fields(model.rvc_species.Sample, self.session)

            class testForm(wtforms.Form):
                pass
            
            expected = ['time', 'date', 'observer', 'site', 'speciesgroup']
            expected = set(expected)

            self.assertIsInstance(fields, OrderedDict)
            self.assertEqual(set(fields.keys()), expected)

            self.assertEqual(fields['observer'].html_attributes,
                             {'data-values_url': '/rvc_species/observer/'})
            self.assertEqual(fields.values()[0], fields['site'])
            self.assertEqual(fields['site'].html_attributes,
                             {'autoFocus': True,
                              'data-values_url': '/rvc_species/site/'})
            
            form = testForm()
            for label, field in fields.items():
                fields[label] = field.bind(form, label)
                self.assertTrue(hasattr(field, 'html_attributes'))
            
            self.assertIsInstance(fields['site'], wtforms.SelectField)
            self.assertIsInstance(fields['observer'], 
                                  wtforms.SelectMultipleField)
            self.assertTrue(hasattr(fields['date'].validators, '__iter__'))

