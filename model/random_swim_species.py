from _base import Base, BaseSample, BaseObservation
from _base import BaseObserver, BaseSpecies, BaseSite
from sqlalchemy import Column, Integer, String, Unicode, Table, Date, Time
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Sample(BaseSample):
    __tablename__ = 'random_swim_species_sample'
    __mapper_args__ = {'polymorphic_identity':'random_swim_species'}
    id = Column(Integer,ForeignKey('base_sample.id'),primary_key=True)

class Observer(BaseObserver):
    __tablename__ = 'random_swim_species_observer'
    __mapper_args__ = {'polymorphic_identity':'random_swim_species'}
    id = Column(Integer,ForeignKey('base_observer.id'),primary_key=True)

class Site(BaseSite):
    __tablename__ = 'random_swim_species_site'
    __mapper_args__ = {'polymorphic_identity':'random_swim_species'}
    id = Column(Integer,ForeignKey('base_site.id'),primary_key=True)

class Species(BaseSpecies):
    __tablename__ = 'random_swim_species_species'
    __mapper_args__ = {'polymorphic_identity':'random_swim_species'}
    id = Column(Integer,ForeignKey('base_species.id'),primary_key=True)

class Observation(BaseObservation):
    __tablename__ = 'random_swim_species_observation'
    __mapper_args__ = {'polymorphic_identity':'random_swim_species'}
    id = Column(Integer,ForeignKey('base_observation.id'),primary_key=True)
    species_id = Column(Integer, ForeignKey("random_swim_species_species.id"))
    species = relationship("model.random_swim_species.Species", backref="observations")
    amount_0_9 = Column(Integer)
    amount_10_19 = Column(Integer)
    amount_20_29 = Column(Integer)
    amount_30_39 = Column(Integer)
    amount_40_49 = Column(Integer)


tables = (Sample, Observer, Observation, Species, Site)
