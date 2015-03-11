from sqlalchemy import Column, Integer, String, Unicode, Table, Date, Time
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

sample_participants = Table("sample_participants",Base.metadata,
    Column("sample_id", Integer, ForeignKey("sample.id")),
    Column("observer_id", Integer, ForeignKey("observer.id"))
)


class BaseSample(Base):
    __tablename__ = 'sample'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    time = Column(Time)
    site_id = Column(Integer, ForeignKey('site.id'))
    site = relationship("Site", backref="samples")
    participants = relationship("Observer",
                        secondary=sample_participants,
                        backref="samples")
    def __str__(self):
        return "Sample %s on %s %s at %s"%(self.id,self.date,self.time or '',self.site.name)


class BaseObserver(Base):
    __tablename__ = "observer"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    def __str__(self):
        return "%s"%self.name


class BaseObservation(Base):
    __tablename__ = "observation"
    id = Column(Integer, primary_key=True)
    observer_id = Column(Integer, ForeignKey("observer.id"))
    sample_id = Column(Integer, ForeignKey("sample.id"))
    sample = relationship("Sample", backref="observations")
    observer = relationship("Observer", backref="observations")
    def __str__(self):
        return "Observation %i on %s at %s"%(self.id,self.sample.date,self.sample.site)



class BaseSite(Base):
    __tablename__ = "site"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    barangay = Column(Unicode)
    municipality = Column(Unicode)
    lat = Column(String)
    lon = Column(String)
    def __str__(self):
        return "%s, %s, %s"%(self.municipality,self.barangay,self.name)
