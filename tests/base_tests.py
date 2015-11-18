import biodata
from unittest import TestCase
from biodata import model
import datetime

class _BaseTest(TestCase):
    """
    unittest.TestCase that sets up a Flask app to interact with form tests.
    """
    
    def setUp(self):
        biodata.app.config['TESTING'] = True
        self.app = biodata.app
        self.client = biodata.app.test_client()
    
    def tearDown(self):
        pass


class _BaseDBTest(_BaseTest):
    """
    unittest.TestCase that sets up the database and creates the tables
    during setUp and drops everything again at tearDown.
    """
    def setUp(self):
        _BaseTest.setUp(self)
        biodata.init_db()
        with biodata.app.app_context():
            speciesgroup = model.rvc_species.SpeciesGroup(name=u'testgroup')
            biodata.db.session.add(speciesgroup)
            site = model.rvc_species.Site(name=u"TestSite")
            biodata.db.session.add(site)
            observer = model.rvc_species.Observer(name=u"Dolf")
            biodata.db.session.add(observer)
            sample = model.rvc_species.Sample()
            sample.date = datetime.datetime.now()
            sample.site = site
            sample.speciesgroup = speciesgroup
            sample.participants.append(observer)
            biodata.db.session.add(sample)
            biodata.db.session.commit()

        
    def tearDown(self):
        with biodata.app.app_context():
            biodata.db.drop_all()