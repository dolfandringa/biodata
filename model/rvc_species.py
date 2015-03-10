from sqlalchemy import Column, Integer, String, Unicode, Table, Date, Time
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

sample_participants = Table("sample_participants",Base.metadata,
    Column("sample_id", Integer, ForeignKey("sample.id")),
    Column("observer_id", Integer, ForeignKey("observer.id"))
)


class Sample(Base):
    __tablename__ = 'sample'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    time = Column(Time)
    site_id = Column(Integer, ForeignKey('site.id'))
    site = relationship("Site", backref="samples")
    participants = relationship("Observer",
                        secondary=sample_participants,
                        backref="samples")


class Observer(Base):
    __tablename__ = "observer"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    observations = relationship("Observation", backref="observer")


class Observation(Base):
    __tablename__ = "observation"
    id = Column(Integer, primary_key=True)
    amount = Column(Integer)
    total_score = Column(Integer)
    score_0_9 = Column(Integer)
    score_10_19 = Column(Integer)
    score_20_29 = Column(Integer)
    score_30_39 = Column(Integer)
    score_40_49 = Column(Integer)
    sample_id = Column(Integer, ForeignKey("sample.id"))
    species_id = Column(Integer, ForeignKey("species.id"))
    observer_id = Column(Integer, ForeignKey("observer.id"))
    sample = relationship("Sample", backref="observations")


class Species(Base):
    __tablename__ = "species"
    id = Column(Integer, primary_key=True)
    common_name = Column(Unicode)
    scientific_name = Column(Unicode)
    observations = relationship("Observation", backref="species")


class Site(Base):
    __tablename__ = "site"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    barangay = Column(Unicode)
    municipality = Column(Unicode)
    lat = Column(String)
    lon = Column(String)


__tables__ = (Sample, Observer, Observation, Species, Site)
