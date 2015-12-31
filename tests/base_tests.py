import biodata
from unittest import TestCase
from biodata import model
import datetime


class _BaseTest(TestCase):
    """
    unittest.TestCase that sets up a Flask app to interact with form tests.
    """

    def setUp(self):
        self.app = biodata.get_app(testing=True)
        self.session = biodata.db.session
        self.client = self.app.test_client()

    def tearDown(self):
        pass


class _BaseDBTest(_BaseTest):
    """
    unittest.TestCase that sets up the database and creates the tables
    during setUp and drops everything again at tearDown.
    """
    def setUp(self):
        _BaseTest.setUp(self)
        biodata.config_db(self.app)
        biodata.bind_db(self.app)
        biodata.setup_db(self.app)
        with self.app.app_context():
            load_data(biodata.db.session)

    def tearDown(self):
        with self.app.app_context():
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
    dolf = model.rvc_species.Observer(name=u'dolf')
    annelies = model.rvc_species.Observer(name=u'annelies')
    add(dolf)
    add(annelies)

    guinsuan = model.rvc_species.Site(name=u'guinsuan')
    add(guinsuan)

    specgroup = model.rvc_species.SpeciesGroup(name=u'TestSpecGroup')
    add(specgroup)

    sample1 = model.rvc_species.Sample()
    sample1.date = datetime.datetime(2015, 11, 18)
    sample1.time = datetime.datetime(2015, 11, 18, 21, 38, 39, 881432)
    sample1.participants = [dolf]
    sample1.site = guinsuan
    sample1.speciesgroup = specgroup
    add(sample1)

    sample2 = model.rvc_species.Sample()
    sample2.date = datetime.datetime(2015, 11, 18)
    sample2.time = datetime.datetime(2015, 11, 18, 21, 38, 40, 882212)
    sample2.participants = [dolf, annelies]
    sample2.site = guinsuan
    sample2.speciesgroup = specgroup
    add(sample2)

    for i in range(10):
        spec = model.rvc_species.Species()
        spec.scientific_name = u'sci%i' % i
        spec.common_name = u'com%i' % i
        add(spec)

    for i in range(10):
        obs = model.rvc_species.Observation()
        obs.sample = sample1
        obs.observer = dolf
        obs.species = session.query(model.rvc_species.Species).get(i)
        add(obs)

    session.commit()
