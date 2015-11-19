from base_tests import _BaseDBTest, _BaseTest
from biodata.controller import show, list, edit, delete, new
import testmodel
import biodata
import os
import re

curdir = os.path.dirname(os.path.abspath(__file__))

class ControllerTest(_BaseDBTest):
    """
    Tests all the controllers by calling them and comparing their output to
    static html files in the html folder.
    """
    
    def setUp(self):
        _BaseDBTest.setUp(self)
        uri = self.app.config['SQLALCHEMY_DATABASE_URI']
    
    def tearDown(self):
        _BaseDBTest.tearDown(self)
    
    def test_list(self):
        """
        Test the list controller without selection parameters.
        """
        r = re.compile("^[\s]+", re.MULTILINE)
        # with self.app.app_context():
        self.maxDiff = None
        response = self.client.get('/rvc_species/sample/')
        self.assertEqual(response.status_code, 200)
        result = response.get_data(as_text = True)
        result = re.sub(r,"",result) #remove whitespace at the beginning of a line
        f= open(os.path.join(curdir, 'html', 'rvc_species', 'sample', 'index.html'),'r')
        expected = f.read()
        expected = re.sub(r,"",expected) #remove whitespace at the beginning of a line
        self.assertMultiLineEqual(expected, result)
            
    
    def test_list_arguments(self):
        """
        Test the list controller with selection parameters.
        """
        self.fail("Not implemented")