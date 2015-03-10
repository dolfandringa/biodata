from _base import Base, BaseSample, BaseObservation
from _base import BaseObserver, BaseSite
from sqlalchemy import Column, Integer, String, Unicode, Table, Date, Time
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Sample(BaseSample):
    amount = Column(Integer)
    total_score = Column(Integer)
    score_0_9 = Column(Integer)
    score_10_19 = Column(Integer)
    score_20_29 = Column(Integer)
    score_30_39 = Column(Integer)
    score_40_49 = Column(Integer)

class Site(BaseSite):
    pass

class Observer(BaseObserver):
    pass

class Observation(BaseObservation):
    species_id = Column(Integer, ForeignKey("species.id"))
    species = relationship("Species", backref="observations")

class Species(Base):
    __tablename__ = "species"
    id = Column(Integer, primary_key=True)
    common_name = Column(Unicode)
    scientific_name = Column(Unicode)

__tables__ = (Sample, Observer, Observation, Species, Site)
