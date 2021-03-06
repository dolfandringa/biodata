from _base import BaseSample, BaseObservation
from _base import BaseSite, BaseSpecies, BaseObserver
from sqlalchemy import Column, Integer, Time, Numeric
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import copy


class Sample(BaseSample):
    __tablename__ = 'clams_sample'
    __mapper_args__ = {'polymorphic_identity': 'clams'}
    id = Column(Integer, ForeignKey('base_sample.id'), primary_key=True)


class Observer(BaseObserver):
    __tablename__ = 'clams_observer'
    __mapper_args__ = {'polymorphic_identity': 'clams'}
    id = Column(Integer, ForeignKey('base_observer.id'), primary_key=True)


class Site(BaseSite):
    __tablename__ = 'clams_site'
    __mapper_args__ = {'polymorphic_identity': 'clams'}
    id = Column(Integer, ForeignKey('base_site.id'), primary_key=True)


class Species(BaseSpecies):
    __tablename__ = 'clams_species'
    __mapper_args__ = {'polymorphic_identity': 'clams'}
    id = Column(Integer, ForeignKey('base_species.id'), primary_key=True)


class Observation(BaseObservation):
    __tablename__ = 'clams_observation'
    __mapper_args__ = {'polymorphic_identity': 'clams'}
    id = Column(Integer, ForeignKey('base_observation.id'), primary_key=True)
    depth = Column(Numeric)
    size = Column(Integer)
    time = Column(Time)
    # deepcopy the formfields so we are not altering the mutable for other
    # BaseObservation instances
    formfields = copy.deepcopy(BaseObservation.formfields)
    formfields['size'] = {'kwargs': {'description': " size in whole cm"}}
    formfields['depth'] = {'kwargs': {'description':
                                      " depth in m (with decimal numbers)"}}
    species_id = Column(Integer, ForeignKey("clams_species.id"))
    species = relationship("model.clams.Species", backref="observations")


tables = (Sample, Observer, Observation, Species, Site)
