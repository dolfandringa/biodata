from base_tests import _BaseDBTest, _BaseTest
import biodata
from biodata import model
from biodata.util import *
from wtforms import ValidationError, Form, StringField
from wtforms.validators import InputRequired
import tempfile
import os
from sqlalchemy import Column, Integer, String, Unicode, Table, Date, Time
from sqlalchemy import ForeignKey, UnicodeText
from sqlalchemy.orm import relationship, declarative_base
import types

Base = declarative_base()

class TestSample(Base):
    __tablename__ = 'testsampe'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=True)
    name = Column(Unicode, nullable=False)


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
        v = validator("Please enter an integer value",isint)
        class TestForm(Form):
            test = StringField('test',[v])
        class TestForm2(Form):
            test = StringField('test',[v,InputRequired()])
        form = TestForm(data={'test':1})
        self.assertTrue(form.validate())
        form = TestForm()
        self.assertTrue(form.validate())
        form = TestForm2()
        self.assertFalse(form.validate())
        form = TestForm(data={'test':'bla'})
        self.assertFalse(form.validate())
    
    def test_map_column_type(self):
        """
        Tests the mapping of column types.
        """
        type = map_column_type(TestSample.id)
        self.assertEqual(type['label'],'id')
        self.assertEqual(type['widget'],wtforms.IntegerField)
        type = map_column_type(TestSample.date)
        self.assertEqual(type['label'],'date')
        self.assertEqual(type['widget'],wtforms.DateField)
        self.assertEqual(type['kwargs']['format'],'%Y-%m-%d')
        self.assertIsInstance(type['args'][0],wtforms.validators.InputRequired)
        type = map_column_type(TestSample.time)
        self.assertEqual(type['label'],'time')
        self.assertEqual(type['widget'],wtforms.DateTimeField)
        self.assertEqual(type['kwargs']['format'],'%H:%M')
        type = map_column_type(TestSample.name)
        self.assertEqual(type['label'],'name')
        self.assertEqual(type['widget'],wtforms.StringField)
        self.assertIsInstance(type['args'][0],wtforms.validators.InputRequired)
        
    def test_get_object(self):
        """
        Test if the biodata.util.get_object function
        returns a correct class based on the name of the dataset and object.
        """
        obj = get_object('rvc_species','sample')
        self.assertEquals(obj, model.rvc_species.Sample)

class UtilTestDB(_BaseDBTest):
    """
    This testcase test the utility functions in biodata.util that need to read
    or write rows to/from the database and thus need an active connection.
    """
    
    def test_get_data_attributes(self):
        """
        Test fetching of sqlalchemy attributes from an SQLAlchemy class
        """
        attrs = get_data_attributes(TestSample)
        self.assertIsInstance(attrs,types.GeneratorType)
        with biodata.app.app_context():
            attrs = list(attrs)
        self.assertEqual(len(attrs),4)
        self.assertEqual(set([a.name for a in attrs]),set(['id','date','time','name']))
    
    