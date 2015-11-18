from base_tests import _BaseDBTest, _BaseTest
from biodata.controller import show, list, edit, delete, new
import testmodel
import biodata

class ControllerTest(_BaseDBTest):
    """
    Tests all the controllers by calling them and comparing their output to
    static html files in the html folder.
    """
    
    def setUp(self):
        _BaseDBTest.setUp(self)
        uri = biodata.app.config['SQLALCHEMY_DATABASE_URI']
    
    def tearDown(self):
        _BaseDBTest.tearDown(self)
    
    def test_list(self):
        """
        Test the list controller without selection parameters.
        """
        self.fail("Not implemented")
    
    def test_list_arguments(self):
        """
        Test the list controller with selection parameters.
        """
        self.fail("Not implemented")