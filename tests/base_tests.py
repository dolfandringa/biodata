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

def setupdb(uri):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(uri)
    model._base.Base.metadata.bind = engine
    model._base.Base.metadata.drop_all()
    model._base.Base.metadata.create_all()
    session = sessionmaker(bind=engine)()
    load_data(session)


def load_data(session):
    """Load test data"""
    add = session.add
    dolf = model.rvc_species.Observer(name = u'dolf')
    annelies = model.rvc_species.Observer(name = u'annelies')
    add(dolf)
    add(annelies)
    
    guinsuan = model.rvc_species.Site(name = u'guinsuan')
    add(guinsuan)
    
    specgroup = model.rvc_species.SpeciesGroup(name = u'TestSpecGroup')
    add(specgroup)
    
    sample1 = model.rvc_species.Sample()
    sample1.date = datetime.datetime.now()
    sample1.time = datetime.datetime.now()
    sample1.participants = [dolf]
    sample1.site = guinsuan
    sample1.speciesgroup = specgroup
    add(sample1)
    
    sample2 = model.rvc_species.Sample()
    sample2.name = u'test2'
    sample2.date = datetime.datetime.now()
    sample2.time = datetime.datetime.now()
    sample2.participants = [dolf, annelies]
    sample2.site = guinsuan
    sample2.speciesgroup = specgroup
    add(sample2)
    
    for i in range(10):
        spec = model.rvc_species.Species()
        spec.scientific_name = 'sci%i'%i
        spec.common_name = 'com%i'%i
        add(spec)
    
    for i in range(10):
        obs = model.rvc_species.Observation()
        obs.sample = sample1
        obs.observer = dolf
        obs.species = session.query(model.rvc_species.Species).get(i)
        add(obs)

    session.commit()