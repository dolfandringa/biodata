import biodata
from unittest import TestCase

class _BaseTest(TestCase):
    """
    unittest.TestCase that sets up a Flask app to interact with form tests.
    """
    
    def setUp(self):
        biodata.app.config['TESTING'] = True
        self.app = biodata.app.test_client()
    
    def tearDown(self):
        pass


class _BaseDBTest(_BaseTest):
    """
    unittest.TestCase that sets up the database and creates the tables
    during setUp and drops everything again at tearDown.
    """
    def setUp(self):
        super(_BaseDBTest,self)
        biodata.init_db()
        #with biodata.app.app_context():
        #    print("db connection: %s"%biodata.db.engine)

        
    def tearDown(self):
        with biodata.app.app_context():
            biodata.db.drop_all()