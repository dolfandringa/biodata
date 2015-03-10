from sqlalchemy import create_engine
import rvc_species
engine = create_engine("postgres://biodata:Ibaethohr7@mcpdesktop/biodata")

if __name__ == "__main__":
    from sqlalchemy.ext.declarative import declarative_base
    rvc_species.Base.metadata.create_all(engine)
