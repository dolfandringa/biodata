#from sqlalchemy import create_engine
#from configparser import SafeConfigParser
import os

#config=SafeConfigParser()
#curdir = os.path.abspath(os.path.dirname(__file__))
#settings_file=os.path.join(curdir,'..','settings.cfg')

import rvc_species
import random_swim_species
import clams

#config.read(settings_file)
#uri=config.get('database','uri')
#engine = create_engine(uri)

datasets = [rvc_species, random_swim_species, clams]

#if __name__ == "__main__":
#    from sqlalchemy.ext.declarative import declarative_base
#    for dataset in datasets:
#        dataset.Base.metadata.create_all(engine)
