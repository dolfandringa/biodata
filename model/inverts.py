from _base import BaseSample, BaseObservation
from _base import BaseSite, BaseSpecies, BaseObserver
from sqlalchemy import Column, Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Sample(BaseSample):
    __tablename__ = 'inverts_sample'
    __mapper_args__ = {'polymorphic_identity': 'inverts'}
    id = Column(Integer, ForeignKey('base_sample.id'), primary_key=True)


class Observer(BaseObserver):
    __tablename__ = 'inverts_observer'
    __mapper_args__ = {'polymorphic_identity': 'inverts'}
    id = Column(Integer, ForeignKey('base_observer.id'), primary_key=True)


class Site(BaseSite):
    __tablename__ = 'inverts_site'
    __mapper_args__ = {'polymorphic_identity': 'inverts'}
    id = Column(Integer, ForeignKey('base_site.id'), primary_key=True)


class Species(BaseSpecies):
    __tablename__ = 'inverts_species'
    __mapper_args__ = {'polymorphic_identity': 'inverts'}
    id = Column(Integer, ForeignKey('base_species.id'), primary_key=True)


class Observation(BaseObservation):
    __tablename__ = 'inverts_observation'
    __mapper_args__ = {'polymorphic_identity': 'inverts'}
    id = Column(Integer, ForeignKey('base_observation.id'), primary_key=True)
    species_id = Column(Integer, ForeignKey("inverts_species.id"))
    species = relationship("model.inverts.Species", backref="observations")
    t0_20 = Column(Integer)
    t25_45 = Column(Integer)
    t50_70 = Column(Integer)
    t75_95 = Column(Integer)
    _auto_add_instance_fields = ['species']

tables = (Sample, Observer, Observation, Species, Site)
