from sqlalchemy import create_engine
from configparser import SafeConfigParser
import rvc_species
config=SafeConfigParser()
config.read('settings.cfg')
uri=config.get('database','uri')
engine = create_engine(uri)

if __name__ == "__main__":
    from sqlalchemy.ext.declarative import declarative_base
    rvc_species.Base.metadata.create_all(engine)
