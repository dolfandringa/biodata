# coding: utf-8
#import csv
import datetime
import sys
import os
from configparser import SafeConfigParser
from collections import OrderedDict
try:
    parentpath=os.path.join(os.path.abspath(os.path.dirname(__file__)),'..')
except:

    parentpath=os.path.abspath(os.getcwd())
sys.path.append(parentpath)
try:
    filename=sys.argv[1]
except:
    pass
#rows=[r for r in csv.reader(open('Butterfly.csv','r'),delimiter=';')]
from odsreader import ODSReader
from model import *
from sqlalchemy.orm import sessionmaker, scoped_session
config=SafeConfigParser()
config.read(os.path.join(parentpath,'settings.cfg'))
print("Reading ods")
reader=ODSReader(filename)
rows=[r for r in reader.getSheet(reader.SHEETS.keys()[0]) if r[2]!=u'']

print("Processing data")
colnames=rows[0][:]
datadict=dict([(k,[]) for k in colnames])
for r in rows[1:]:
    for i,c in enumerate(colnames):
        datadict[c].append(r[i])
observers=OrderedDict([(s,i) for i,s in enumerate(set(datadict['Observer']))])
sites=OrderedDict([(s,i) for i,s in enumerate(set(datadict['Site']))])
species=OrderedDict([(s,i) for i,s in enumerate(set(zip(datadict['Common'],datadict['Scientific'])))])
if ('Spot-tail butterflyfish', 'Chaetodon ocellicuadus') in species.keys():
    species[('Spot-tail butterflyfish', 'Chaetodon ocellicuadus')]=species[('Spot-tail butterflyfish', 'Chaetodon ocellicaudus')]
if ('Oval-Spot Butterfly', 'Chaetodon speculum') in species.keys():
    species[('Oval-Spot Butterfly', 'Chaetodon speculum')]=species[('Oval-Spot Butterflyfish', 'Chaetodon speculum')]
species_common=OrderedDict([(k[0],v) for k,v in species.items()])
species_scientific=OrderedDict([(k[1],v) for k,v in species.items()])
samples = []
for i,val in enumerate(zip(datadict['Date'],datadict['Time in'],datadict['Site'])):
    samples.append((val,i))
samples.sort(key=lambda x: datetime.datetime.strptime(x[0][0]+' '+(x[0][1] or '00h00'),'%Y-%m-%d %Hh%M'))
samples=OrderedDict(set(samples))
samples2=OrderedDict()
for k,v in samples.items():
    samples2[v]={
                        'id':v,
                        'site_id':sites[k[2]],
                        'time':k[1] and datetime.datetime.strptime(k[1],'%Hh%M').time() or None,
                        'date':datetime.datetime.strptime(k[0],'%Y-%m-%d'),
                        'participants':set()
                    }

observations=[]
for r in range(len(rows[1:])):
    d={}
    d['id']=r
    d['species_id']=species_scientific[datadict['Scientific'][r]]
    d['observer_id']=observers[datadict['Observer'][r]]
    d['sample_id']=samples[(datadict['Date'][r],datadict['Time in'][r],datadict['Site'][r])]
    d['score_0_9']=datadict['0-10 min'][r]
    d['score_10_19']=datadict['11-20 min'][r]
    d['score_20_29']=datadict['21-30 min'][r]
    d['score_30_39']=datadict['31-40 min'][r]
    d['score_40_49']=datadict['41-50 min'][r]
    d['comments']=datadict['Comments'][r]
    samples2[samples[(datadict['Date'][r],datadict['Time in'][r],datadict['Site'][r])]]['participants'].add(observers[datadict['Observer'][r]])
    observations.append(d)
filter(lambda x: x[0]!=x[1],zip([s['species_id'] for s in observations],[species_common[r] for i,r in enumerate(datadict['Common'])]))
filter(lambda x: x[0]!=x[1],zip([s['sample_id'] for s in observations],[samples[(datadict['Date'][i],datadict['Time in'][i],datadict['Site'][i])] for i in range(len(rows[1:]))]))

sites2=[]
for k,v in sites.items():
    sites2.append({'id':v,'name':k})
observers2=[]
for k,v in observers.items():
    observers2.append({'id':v,'name':k})
species2=[]
for k,v in species.items():
    species2.append({'id':v,'scientific_name':k[1],'common_name':k[0]})

print("Setting up database connection")
engine = create_engine(config.get('database','uri'))
rvc_species.Base.metadata.create_all(engine)
session=scoped_session(sessionmaker(bind=engine))

id_map={'species':{},'sites':{},'samples':{},'observers':{},'observations':{}}
print("Uploading data")
added_sites=0
for x in sites2:
    s=session.query(rvc_species.Site).filter_by(name=x['name']).first()
    if not s:
        s=rvc_species.Site()
        s.name=x['name']
        session.add(s)
        added_sites+=1
    id_map['sites'][x['id']]=s

session.commit()

added_observers=0
for observer in observers2:
    s=session.query(rvc_species.Observer).filter_by(name=observer['name']).first()
    if not s:
        s=rvc_species.Observer()
        s.name=observer['name']
        session.add(s)
        added_observers+=1
    id_map['observers'][observer['id']]=s

session.commit()

added_samples=0
for sample in samples2.values():
    site=id_map['sites'][sample['site_id']]
    s=session.query(rvc_species.Sample).filter_by(date=sample['date'],time=sample['time'],site=site).first()
    if not s:
        s=rvc_species.Sample()
        s.date=sample['date']
        s.time=sample['time']
        session.add(s)
        s.site=site
        s.participants=[id_map['observers'][i] for i in sample['participants']]
        added_samples+=1
    id_map['samples'][sample['id']]=s

session.commit()

added_species=0
for x in species2:
    s=session.query(rvc_species.Species).filter_by(common_name=x['common_name'],scientific_name=x['scientific_name']).first()
    if not s:
        s=rvc_species.Species()
        s.common_name=x['common_name']
        s.scientific_name=x['scientific_name']
        session.add(s)
        added_species+=1
    if x['id'] not in id_map['species'].keys():
        id_map['species'][x['id']]=s

session.commit()

added_observations=0
for x in observations:
    species_id=id_map['species'][x['species_id']].id
    sample_id=id_map['samples'][x['sample_id']].id
    observer_id=id_map['observers'][x['observer_id']].id
    s=session.query(rvc_species.Observation).filter_by(sample_id=sample_id,species_id=species_id,observer_id=observer_id).first()
    if not s:
        s=rvc_species.Observation()
        session.add(s)
        s.species = id_map['species'][x['species_id']]
        s.observer = id_map['observers'][x['observer_id']]
        s.sample = id_map['samples'][x['sample_id']]
        s.score_0_9 = x['score_0_9'].isdigit() and x['score_0_9'] or 0
        s.score_10_19 = x['score_10_19'].isdigit() and x['score_10_19'] or 0
        s.score_20_29 = x['score_20_29'].isdigit() and x['score_20_29'] or 0
        s.score_30_39 = x['score_30_39'].isdigit() and x['score_30_39'] or 0
        s.score_40_49 = x['score_40_49'].isdigit() and x['score_40_49'] or 0
        s.comments = x['comments'] or None
        added_observations+=1
    if x['id'] not in id_map['observations'].keys():
        id_map['observations'][x['id']]=s

session.commit()
print("Added observations: %s\nAdded species: %s\nAdded sites: %s\nAdded samples: %s"%(added_observations,added_species,added_sites,added_samples))
print("Done")


