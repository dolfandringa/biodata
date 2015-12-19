"""Rename species_group

Revision ID: e7f256a43ab
Revises: 447417541260
Create Date: 2015-09-24 09:22:46.421422

"""
import copy
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e7f256a43ab'
down_revision = '447417541260'
branch_labels = None
depends_on = None


old_views = {
    'duplicate_samples': """SELECT s.id AS sample_id,
        s.num_occurence,
        s.date,
        s."time",
        (((base_site.name::text || ', '::text) || base_site.barangay::text) || ', '::text) || base_site.municipality::text,
        s.dataset
       FROM ( SELECT count(base_sample.id) OVER (PARTITION BY rvc_species_sample.species_group_id, base_sample.dataset, base_sample.date, base_sample."time", base_sample.site_id) AS num_occurence,
                base_sample.id,
                base_sample.date,
                base_sample."time",
                base_sample.site_id,
                base_sample.dataset,
                rvc_species_sample.species_group_id
               FROM base_sample
                 LEFT JOIN rvc_species_sample USING (id)) s
         LEFT JOIN base_site ON s.site_id = base_site.id
      WHERE s.num_occurence > 1;""",

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
         LEFT JOIN rvc_species_speciesgroup ON rvc_species_sample.species_group_id = rvc_species_speciesgroup.id
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
         LEFT JOIN rvc_species_speciesgroup ON rvc_species_sample.species_group_id = rvc_species_speciesgroup.id
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
            s.observation_id
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
                    count(rvc_species_observation.id) OVER (PARTITION BY rvc_species_observation.species_id, base_observation.sample_id, base_observation.observer_id, rvc_species_observation.score_0_9, rvc_species_observation.score_10_19, rvc_species_observation.score_20_29, rvc_species_observation.score_30_39, rvc_species_observation.score_40_49) AS num_identical_occurence
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

new_views = copy.deepcopy(old_views)
new_views['duplicate_samples'] = """SELECT s.id AS sample_id,
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
      WHERE s.num_occurence > 1;"""
new_views['rvc_species_observations'] = """SELECT base_sample.id AS sample_id,
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
      ORDER BY rvc_species_speciesgroup.name, base_sample.date, base_sample.id, base_observer.id, base_observation.id;"""
new_views['rvc_species_sites'] = """SELECT base_site.name AS site,
        rvc_species_speciesgroup.name AS species_group,
        base_site.barangay,
        base_site.municipality,
        count(DISTINCT base_sample.id) AS number_of_samples
       FROM rvc_species_sample
         LEFT JOIN rvc_species_speciesgroup ON rvc_species_sample.speciesgroup_id = rvc_species_speciesgroup.id
         LEFT JOIN base_sample ON base_sample.id = rvc_species_sample.id
         LEFT JOIN base_site ON base_sample.site_id = base_site.id
      GROUP BY base_site.id, base_site.name, base_site.barangay, base_site.municipality, rvc_species_speciesgroup.name;"""
new_views['small_samples'] = """SELECT
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
           LEFT JOIN rvc_species_speciesgroup ON rvc_species_speciesgroup.id=rvc_species_sample.speciesgroup_id
        GROUP BY base_sample.id,date,time,site, base_observation.dataset, observer, species_group) s
        WHERE max_observations_sample<12"""
new_views['rvc_species_samples'] = """
         SELECT
            base_sample.id as sample_id,
            base_site.id as site_id,
            base_site.name AS site,
            base_sample.date,
            base_sample."time",
            rvc_species_speciesgroup.name AS species_group,
            array_agg(DISTINCT participants.name) AS participants
           FROM rvc_species_sample
             LEFT JOIN rvc_species_speciesgroup ON rvc_species_sample.speciesgroup_id = rvc_species_speciesgroup.id
             LEFT JOIN base_sample ON base_sample.id = rvc_species_sample.id
             LEFT JOIN base_site ON base_sample.site_id = base_site.id
             LEFT JOIN sample_participants ON sample_participants.sample_id = base_sample.id
             LEFT JOIN base_observer participants ON sample_participants.observer_id = participants.id
          GROUP BY base_site.id, base_site.name, rvc_species_speciesgroup.name, base_sample.id, base_sample.date, base_sample."time"
          ORDER BY base_sample.date, base_sample."time", rvc_species_speciesgroup.name, base_site.name"""


def upgrade():
    # commands auto generated by Alembic - please adjust! ###
    for view_name in old_views.keys():
        op.execute("DROP VIEW IF EXISTS %s CASCADE" % view_name)
    op.add_column('rvc_species_sample',
                  sa.Column('speciesgroup_id', sa.Integer(), nullable=True))
    op.execute(
        "UPDATE rvc_species_sample SET speciesgroup_id=species_group_id")
    op.alter_column('rvc_species_sample', 'speciesgroup_id', nullable=False)
    op.drop_constraint(
        u'rvc_species_sample_species_group_id_fkey',
        'rvc_species_sample',
        type_='foreignkey')
    op.create_foreign_key(
        None,
        'rvc_species_sample',
        'rvc_species_speciesgroup',
        ['speciesgroup_id'], ['id'])
    op.drop_column('rvc_species_sample', 'species_group_id')
    for view_name, sql in new_views.items():
        op.execute('CREATE VIEW %s AS %s;' % (view_name, sql))
    # end Alembic commands ###


def downgrade():
    # commands auto generated by Alembic - please adjust! ###
    for view_name in new_views.keys():
        op.execute("DROP VIEW IF EXISTS %s CASCADE" % view_name)
    op.add_column(
        'rvc_species_sample',
        sa.Column('species_group_id',
                  sa.INTEGER(),
                  autoincrement=False,
                  nullable=True))
    op.execute(
        "UPDATE rvc_species_sample SET species_group_id=speciesgroup_id")
    op.alter_column(
        'rvc_species_sample',
        'species_group_id',
        nullable=False)
    op.drop_constraint(u'rvc_species_sample_speciesgroup_id_fkey',
                       'rvc_species_sample',
                       type_='foreignkey')
    op.create_foreign_key(u'rvc_species_sample_species_group_id_fkey',
                          'rvc_species_sample',
                          'rvc_species_speciesgroup',
                          ['species_group_id'],
                          ['id'])
    op.drop_column('rvc_species_sample', 'speciesgroup_id')
    for view_name, sql in old_views.items():
        op.execute('CREATE VIEW %s AS %s;' % (view_name, sql))
    # end Alembic commands ###
