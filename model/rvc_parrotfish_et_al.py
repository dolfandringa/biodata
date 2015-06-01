from _base import Base, BaseSample, BaseObservation
from _base import BaseSite, BaseSpecies, BaseObserver
from sqlalchemy import Column, Integer, String, Unicode, Table, Date, Time
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Sample(BaseSample):
    __tablename__ = 'rvc_parrotfish_et_al_sample'
    __mapper_args__ = {'polymorphic_identity':'rvc_parrotfish_et_al'}
    id = Column(Integer,ForeignKey('base_sample.id'),primary_key=True)

class Observer(BaseObserver):
    __tablename__ = 'rvc_parrotfish_et_al_observer'
    __mapper_args__ = {'polymorphic_identity':'rvc_parrotfish_et_al'}
    id = Column(Integer,ForeignKey('base_observer.id'),primary_key=True)

class Site(BaseSite):
    __tablename__ = 'rvc_parrotfish_et_al_site'
    __mapper_args__ = {'polymorphic_identity':'rvc_parrotfish_et_al'}
    id = Column(Integer,ForeignKey('base_site.id'),primary_key=True)

class Species(BaseSpecies):
    __tablename__ = 'rvc_parrotfish_et_al_species'
    __mapper_args__ = {'polymorphic_identity':'rvc_parrotfish_et_al'}
    id = Column(Integer,ForeignKey('base_species.id'),primary_key=True)

class Observation(BaseObservation):
    __tablename__ = 'rvc_parrotfish_et_al_observation'
    __mapper_args__ = {'polymorphic_identity':'rvc_parrotfish_et_al'}
    id = Column(Integer,ForeignKey('base_observation.id'),primary_key=True)
    species_id = Column(Integer, ForeignKey("rvc_parrotfish_et_al_species.id"))
    species = relationship("model.rvc_parrotfish_et_al.Species", backref="observations")
    score_0_9 = Column(Integer)
    score_10_19 = Column(Integer)
    score_20_29 = Column(Integer)
    score_30_39 = Column(Integer)
    score_40_49 = Column(Integer)

tables = (Sample, Observer, Observation, Species, Site)
