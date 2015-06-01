from sqlalchemy import create_engine
from configparser import SafeConfigParser
import rvc_species
import random_swim_species
config=SafeConfigParser()
config.read('settings.cfg')
uri=config.get('database','uri')
engine = create_engine(uri)

datasets = [rvc_species, random_swim_species]

if __name__ == "__main__":
    from sqlalchemy.ext.declarative import declarative_base
    for dataset in datasets:
        dataset.Base.metadata.create_all(engine)
