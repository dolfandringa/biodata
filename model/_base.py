from sqlalchemy import Column, Integer, String, Unicode, Table, Date, Time
from sqlalchemy import ForeignKey, UnicodeText
from sqlalchemy.orm import relationship
import wtforms
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

Base = db.Model

sample_participants = Table(
    "sample_participants",
    Base.metadata,
    Column("sample_id", Integer, ForeignKey("base_sample.id")),
    Column("observer_id", Integer, ForeignKey("base_observer.id"))
)


class BaseSample(Base):
    """
    These are SQLAlchemy Declarative objects with a few additions.
    The fields for each object are just defined as a column of a certain type.
    This is basic SQLAlchemy notation. The same holds for relationships.

    The following are extra attributes added for the automatic display and
    rendering of the form:

    Formfields is a dictionary where the keys match a field, and the value of
    the dict is another dict with parameters for that field. For now the
    parameters are:
        skip: boolean. If true, this field will not be included in the form.
        widget: a string specifying the wtform field type.
        html_attributes: attributes that are used when rendering the form field
            to add extra html attributes to the tag.
        kwargs: extra keyword arguments to the wtforms field, needed for
            rendering

    _sort is a list specifying which fields should be used for sorting the
    object in lists. Each list item is a tuple with the first item the field
    name and the second item a boolean specifying if the field should be orderd
    in descending order (if False it will be ordered in ascending order).

    _auto_add_instance_fields is a list of relation attributes for which an
    instance of this class needs to be shown in the form. Multiple relation
    attributes can be specified to render a form row of each of the possible
    combinations of the fields in _auto_add_instance_fields.
    As an example, let's say the Observation class has an attribute species
    pointing to a Species class, specifying species in the
    _auto_add_instance_fields list of Observation will make the form where
    observations are added automatically be filled with a row for each value of
    the Species object.
    """
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
    _sort = [('date', True), ('time', True)]
    _auto_add_instance_fields = []

    def __str__(self):
        return "%s at %s" % (self.id, self.site.name)


class BaseObserver(Base):
    __tablename__ = "base_observer"
    pretty_name = 'observer'
    formfields = {}
    _sort = [('name', False)]
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)

    dataset = Column(Unicode)
    __mapper_args__ = {'polymorphic_identity': 'base',
                       'polymorphic_on': dataset}
    formfields['dataset'] = {'skip': True}
    _auto_add_instance_fields = []

    def __str__(self):
        return "%s" % self.name


class BaseObservation(Base):
    __tablename__ = "base_observation"
    pretty_name = 'observation'
    formfields = {}
    _sort = [('id', False)]
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
    _auto_add_instance_fields = []

    def __str__(self):
        return "Observation %i on %s at %s" % (self.id,
                                               self.sample.date,
                                               self.sample.site)


class BaseSite(Base):
    __tablename__ = "base_site"
    pretty_name = 'site'
    formfields = {}
    _sort = [('municipality', False), ('barangay', False), ('name', False)]
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
    _auto_add_instance_fields = []

    def __str__(self):
        return "%s, %s, %s" % (self.name,
                               self.barangay or '',
                               self.municipality or '')


class BaseSpecies(Base):
    __tablename__ = "base_species"
    pretty_name = 'species'
    formfields = {}
    _sort = [('common_name', False)]
    id = Column(Integer, primary_key=True)
    common_name = Column(Unicode)
    scientific_name = Column(Unicode)

    dataset = Column(Unicode)
    __mapper_args__ = {'polymorphic_identity': 'base',
                       'polymorphic_on': dataset}
    formfields['dataset'] = {'skip': True}
    _auto_add_instance_fields = []

    def __str__(self):
        return self.common_name
