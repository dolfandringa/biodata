views = {
    'duplicate_samples': """SELECT s.id AS sample_id,
        s.num_occurence,
        s.date,
        s."time",
        (((base_site.name::text || ', '::text) || base_site.barangay::text) || ', '::text) || base_site.municipality::text as site,
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

    'random_swim_species_sites': """SELECT base_site.name AS site,
        base_site.barangay,
        base_site.municipality,
        count(DISTINCT base_sample.id) AS number_of_samples
       FROM random_swim_species_sample
         LEFT JOIN base_sample ON base_sample.id = random_swim_species_sample.id
         LEFT JOIN base_site ON base_sample.site_id = base_site.id
      GROUP BY base_site.id, base_site.name, base_site.barangay, base_site.municipality;""",

    'rvc_species_observations': """SELECT base_sample.id AS sample_id,
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

    'rvc_species_sites': """SELECT base_site.name AS site,
        rvc_species_speciesgroup.name AS species_group,
        base_site.barangay,
        base_site.municipality,
        count(DISTINCT base_sample.id) AS number_of_samples
       FROM rvc_species_sample
         LEFT JOIN rvc_species_speciesgroup ON rvc_species_sample.speciesgroup_id = rvc_species_speciesgroup.id
         LEFT JOIN base_sample ON base_sample.id = rvc_species_sample.id
         LEFT JOIN base_site ON base_sample.site_id = base_site.id
      GROUP BY base_site.id, base_site.name, base_site.barangay, base_site.municipality, rvc_species_speciesgroup.name;""",

    'small_samples': """SELECT
            *
        FROM
        (SELECT count(base_observation.id) as num_observations,
            max(count(base_observation.id)) OVER (PARTITION BY base_sample.id) as max_observations_sample,
            base_sample.id as sample_id,
            base_sample.date,
            base_sample."time",
            base_site.name as site,
            base_observer.name as observer,
            array_agg(distinct participants.name) as participants,
            rvc_species_speciesgroup.name as species_group,
            base_observation.dataset
           FROM base_sample
           LEFT JOIN sample_participants ON base_sample.id=sample_participants.sample_id
           LEFT JOIN base_observation ON base_observation.sample_id=base_sample.id
           LEFT JOIN rvc_species_observation ON (base_observation.id=rvc_species_observation.id)
           LEFT JOIN rvc_species_sample ON rvc_species_sample.id=base_sample.id
           LEFT JOIN base_observer ON base_observer.id=base_observation.observer_id
           LEFT JOIN base_observer as participants ON participants.id=sample_participants.observer_id
           LEFT JOIN base_site ON base_sample.site_id = base_site.id
           LEFT JOIN rvc_species_speciesgroup ON rvc_species_speciesgroup.id=rvc_species_sample.species_group_id
        GROUP BY base_sample.id,date,time,site, base_observation.dataset, observer, species_group) s
        WHERE max_observations_sample<12""",

    'duplicate_observations': """SELECT s.sample_id,
            base_sample.date,
            base_site.name AS site,
            base_observer.name AS observer,
            base_species.common_name AS species,
            s.species_id,
            s.score_0_9,
            s.score_10_19,
            s.score_20_29,
            s.score_30_39,
            s.score_40_49,
            s.num_occurence,
            s.num_identical_occurence,
            s.observation_id,
            s.identical_observation
           FROM ( SELECT base_observation.sample_id,
                    base_observation.observer_id,
                    rvc_species_observation.species_id,
                    rvc_species_observation.score_0_9,
                    rvc_species_observation.score_10_19,
                    rvc_species_observation.score_20_29,
                    rvc_species_observation.score_30_39,
                    rvc_species_observation.score_40_49,
                    rvc_species_observation.id AS observation_id,
                    count(rvc_species_observation.id) OVER (PARTITION BY rvc_species_observation.species_id, base_observation.sample_id, base_observation.observer_id) AS num_occurence,
                    count(rvc_species_observation.id) OVER (PARTITION BY rvc_species_observation.species_id, base_observation.sample_id, base_observation.observer_id, rvc_species_observation.score_0_9, rvc_species_observation.score_10_19, rvc_species_observation.score_20_29, rvc_species_observation.score_30_39, rvc_species_observation.score_40_49) AS num_identical_occurence,
                    min(rvc_species_observation.id) OVER (PARTITION BY rvc_species_observation.species_id, base_observation.sample_id, base_observation.observer_id, rvc_species_observation.score_0_9, rvc_species_observation.score_10_19, rvc_species_observation.score_20_29, rvc_species_observation.score_30_39, rvc_species_observation.score_40_49) AS identical_observation
                   FROM rvc_species_observation
                     LEFT JOIN base_observation USING (id)) s
             LEFT JOIN base_sample ON s.sample_id = base_sample.id
             LEFT JOIN base_species ON s.species_id = base_species.id
             LEFT JOIN base_observer ON s.observer_id = base_observer.id
             LEFT JOIN base_site ON base_sample.site_id = base_site.id
          WHERE s.num_occurence > 1
          ORDER BY s.sample_id, s.observer_id""",

    'rvc_species_samples': """
         SELECT
            base_sample.id as sample_id,
            base_site.id as site_id,
            base_site.name AS site,
            base_sample.date,
            base_sample."time",
            rvc_species_speciesgroup.name AS species_group,
            array_agg(DISTINCT participants.name) AS participants
           FROM rvc_species_sample
             LEFT JOIN rvc_species_speciesgroup ON rvc_species_sample.species_group_id = rvc_species_speciesgroup.id
             LEFT JOIN base_sample ON base_sample.id = rvc_species_sample.id
             LEFT JOIN base_site ON base_sample.site_id = base_site.id
             LEFT JOIN sample_participants ON sample_participants.sample_id = base_sample.id
             LEFT JOIN base_observer participants ON sample_participants.observer_id = participants.id
          GROUP BY base_site.id, base_site.name, rvc_species_speciesgroup.name, base_sample.id, base_sample.date, base_sample."time"
          ORDER BY base_sample.date, base_sample."time", rvc_species_speciesgroup.name, base_site.name""",
  }
