from sqlalchemy import Column, Integer, String, Unicode, Table, Date, Time
from sqlalchemy import ForeignKey, UnicodeText
from sqlalchemy.orm import relationship
import wtforms
from biodata import db

Base = db.Model

sample_participants = Table(
    "sample_participants",
    Base.metadata,
    Column("sample_id", Integer, ForeignKey("base_sample.id")),
    Column("observer_id", Integer, ForeignKey("base_observer.id"))
)


class BaseSample(Base):
    __tablename__ = 'base_sample'
    pretty_name = 'sample'
    formfields = {}
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=True)
    site_id = Column(Integer, ForeignKey('base_site.id'), nullable=False)
    site = relationship("BaseSite", backref="samples")
    dataset = Column(Unicode)
    participants = relationship(
        "BaseObserver",
        secondary=sample_participants,
        backref="samples")

    dataset = Column(Unicode)
    __mapper_args__ = {'polymorphic_identity': 'base',
                       'polymorphic_on': dataset}
    formfields['dataset'] = {'skip': True}

    def __str__(self):
        return "%s at %s" % (self.id, self.site.name)


class BaseObserver(Base):
    __tablename__ = "base_observer"
    pretty_name = 'observer'
    formfields = {}
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)

    dataset = Column(Unicode)
    __mapper_args__ = {'polymorphic_identity': 'base',
                       'polymorphic_on': dataset}
    formfields['dataset'] = {'skip': True}

    def __str__(self):
        return "%s" % self.name


class BaseObservation(Base):
    __tablename__ = "base_observation"
    pretty_name = 'observation'
    formfields = {}
    id = Column(Integer, primary_key=True)
    comments = Column(UnicodeText)
    observer_id = Column(Integer, ForeignKey("base_observer.id"))
    sample_id = Column(Integer, ForeignKey("base_sample.id"))
    sample = relationship("BaseSample", backref="observations")
    formfields['sample'] = {'widget': wtforms.HiddenField,
                            'valuefunc': lambda x: x.sample.id,
                            'args': [],
                            'kwargs': {}}
    observer = relationship("BaseObserver", backref="observations")

    dataset = Column(Unicode)
    __mapper_args__ = {'polymorphic_identity': 'base',
                       'polymorphic_on': dataset}
    formfields['dataset'] = {'skip': True}

    def __str__(self):
        return "Observation %i on %s at %s" % (self.id,
                                               self.sample.date,
                                               self.sample.site)


class BaseSite(Base):
    __tablename__ = "base_site"
    pretty_name = 'site'
    formfields = {}
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)
    barangay = Column(Unicode)
    municipality = Column(Unicode)
    lat = Column(String)
    lon = Column(String)

    dataset = Column(Unicode)
    __mapper_args__ = {'polymorphic_identity': 'base',
                       'polymorphic_on': dataset}
    formfields['dataset'] = {'skip': True}

    def __str__(self):
        return "%s, %s, %s" % (self.name,
                               self.barangay or '',
                               self.municipality or '')


class BaseSpecies(Base):
    __tablename__ = "base_species"
    pretty_name = 'species'
    formfields = {}
    id = Column(Integer, primary_key=True)
    common_name = Column(Unicode)
    scientific_name = Column(Unicode)

    dataset = Column(Unicode)
    __mapper_args__ = {'polymorphic_identity': 'base',
                       'polymorphic_on': dataset}
    formfields['dataset'] = {'skip': True}

    def __str__(self):
        return self.common_name
