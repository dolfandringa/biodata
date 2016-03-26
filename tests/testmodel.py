from sqlalchemy import Column, Integer, Unicode, Table, Date, Time
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import wtforms

Base = declarative_base()

sample_participants = Table(
    "testsample_testparticipants",
    Base.metadata,
    Column("testsample_id", Integer, ForeignKey("testsample.id")),
    Column("testparticipant_id", Integer, ForeignKey("testparticipant.id"))
)


class TestParticipant(Base):
    __tablename__ = 'testparticipant'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)


class TestSample(Base):
    __tablename__ = 'testsample'
    formfields = {}
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=True)
    hiddentime = Column(Integer)
    name = Column(Unicode, nullable=False)
    hiddenname = Column(Unicode, nullable=False)
    participants = relationship("TestParticipant",
                                secondary=sample_participants,
                                backref="testsamples")
    formfields['hiddentime'] = {'skip': True}
    formfields['hiddenname'] = {'widget': wtforms.HiddenField,
                                'valuefunc': lambda x: x.sample.id,
                                'args': [],
                                'kwargs': {}}


class TestObservation(Base):
    __tablename__ = 'testobservation'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)
    sample_id = Column(Integer, ForeignKey('testsample.id'), nullable=False)
    sample = relationship("TestSample", backref="observations")
    _show_all_fields = ['name']
