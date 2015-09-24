views={
    'duplicate_samples': """SELECT s.id AS sample_id,
        s.num_occurence,
        s.date,
        s."time",
        (((base_site.name::text || ', '::text) || base_site.barangay::text) || ', '::text) || base_site.municipality::text,
        s.dataset
       FROM ( SELECT count(base_sample.id) OVER (PARTITION BY rvc_species_sample.speciesgroup_id, base_sample.dataset, base_sample.date, base_sample."time", base_sample.site_id) AS num_occurence,
                base_sample.id,
                base_sample.date,
                base_sample."time",
                base_sample.site_id,
                base_sample.dataset,
                rvc_species_sample.speciesgroup_id
               FROM base_sample
                 LEFT JOIN rvc_species_sample USING (id)) s
         LEFT JOIN base_site ON s.site_id = base_site.id
      WHERE s.num_occurence > 1;""",
    
    'duplicate_species': """SELECT s.id,
        s.dataset,
        s.num_occurence_common,
        s.num_occurence_scientific,
        s.common_name,
        s.scientific_name
       FROM ( SELECT base_species.id,
                base_species.dataset,
                count(base_species.id) OVER (PARTITION BY base_species.dataset, replace(replace(lower(base_species.common_name::text), ' '::text, ''::text), '-'::text, ''::text)) AS num_occurence_common,
                count(base_species.id) OVER (PARTITION BY base_species.dataset, replace(replace(lower(base_species.scientific_name::text), ' '::text, ''::text), '-'::text, ''::text)) AS num_occurence_scientific,
                base_species.common_name,
                base_species.scientific_name
               FROM base_species) s
      WHERE s.num_occurence_common > 1 OR s.num_occurence_scientific > 1;""",
    
    'random_swim_species_observations': """SELECT base_sample.id AS sample_id,
        base_observation.id AS observation_id,
        base_site.name AS site,
        base_site.barangay,
        base_site.municipality,
        base_site.id AS site_id,
        base_sample.date,
        base_sample."time",
        base_observer.id AS observer_id,
        base_observer.name AS observer,
        base_species.id AS species_id,
        base_species.common_name,
        base_species.scientific_name,
        random_swim_species_observation.amount_0_9,
        random_swim_species_observation.amount_10_19,
        random_swim_species_observation.amount_20_29,
        random_swim_species_observation.amount_30_39,
        random_swim_species_observation.amount_40_49
       FROM random_swim_species_observation
         LEFT JOIN base_observation ON base_observation.id = random_swim_species_observation.id
         LEFT JOIN random_swim_species_sample ON random_swim_species_sample.id = base_observation.sample_id
         LEFT JOIN base_sample ON base_sample.id = base_observation.sample_id
         LEFT JOIN base_observer ON base_observer.id = base_observation.observer_id
         LEFT JOIN base_site ON base_sample.site_id = base_site.id
         LEFT JOIN base_species ON base_species.id = random_swim_species_observation.species_id
      ORDER BY base_sample.date, base_sample.id, base_observer.id;""",
      
      'random_swim_species_sites':"""SELECT base_site.name AS site,
        base_site.barangay,
        base_site.municipality,
        count(DISTINCT base_sample.id) AS number_of_samples
       FROM random_swim_species_sample
         LEFT JOIN base_sample ON base_sample.id = random_swim_species_sample.id
         LEFT JOIN base_site ON base_sample.site_id = base_site.id
      GROUP BY base_site.id, base_site.name, base_site.barangay, base_site.municipality;""",
      
      'rvc_species_observations':"""SELECT base_sample.id AS sample_id,
        base_observation.id AS observation_id,
        base_site.name AS site,
        base_site.barangay,
        base_site.municipality,
        base_site.id AS site_id,
        base_sample.date,
        base_sample."time",
        rvc_species_speciesgroup.name AS species_group,
        base_observer.id AS observer_id,
        base_observer.name AS observer,
        base_species.id AS species_id,
        base_species.common_name,
        base_species.scientific_name,
        rvc_species_observation.score_0_9,
        rvc_species_observation.score_10_19,
        rvc_species_observation.score_20_29,
        rvc_species_observation.score_30_39,
        rvc_species_observation.score_40_49
       FROM rvc_species_observation
         LEFT JOIN base_observation ON base_observation.id = rvc_species_observation.id
         LEFT JOIN rvc_species_sample ON rvc_species_sample.id = base_observation.sample_id
         LEFT JOIN rvc_species_speciesgroup ON rvc_species_sample.speciesgroup_id = rvc_species_speciesgroup.id
         LEFT JOIN base_sample ON base_sample.id = base_observation.sample_id
         LEFT JOIN base_observer ON base_observer.id = base_observation.observer_id
         LEFT JOIN base_site ON base_sample.site_id = base_site.id
         LEFT JOIN base_species ON base_species.id = rvc_species_observation.species_id
      ORDER BY rvc_species_speciesgroup.name, base_sample.date, base_sample.id, base_observer.id, base_observation.id;""",
      
      'rvc_species_sites':"""SELECT base_site.name AS site,
        rvc_species_speciesgroup.name AS species_group,
        base_site.barangay,
        base_site.municipality,
        count(DISTINCT base_sample.id) AS number_of_samples
       FROM rvc_species_sample
         LEFT JOIN rvc_species_speciesgroup ON rvc_species_sample.speciesgroup_id = rvc_species_speciesgroup.id
         LEFT JOIN base_sample ON base_sample.id = rvc_species_sample.id
         LEFT JOIN base_site ON base_sample.site_id = base_site.id
      GROUP BY base_site.id, base_site.name, base_site.barangay, base_site.municipality, rvc_species_speciesgroup.name;""",
      
  }