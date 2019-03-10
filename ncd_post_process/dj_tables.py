import datajoint as dj

SCHEMA_NAME = 'dj_ncd'

dj.config['database.host'] = '127.0.0.1'
dj.config['database.user'] = 'root'
dj.config['database.password'] = 'pw4pblab'
dj.config['external-raw'] = {
    'protocol': 'file',
    'location': f'/data/neural_collision_detection/datajoint/data/{SCHEMA_NAME}'
}
schema = dj.schema(SCHEMA_NAME, locals())

@schema
class VasculatureData(dj.Manual):
    definition = """
    vasc_id: smallint unsigned
    ---
    fname: varchar(1000)
    """


@schema
class CellCenters(dj.Manual):
    definition = """
    centers_id: smallint unsigned
    -> VasculatureData
    ---
    fname: varchar(1000)
    layer: enum('I', 'II_III', 'IV', 'V', 'VI')
    """


@schema
class Neuron(dj.Manual):
    definition = """
    neuron_id: smallint unsigned
    ---
    name: varchar(25)
    fname: varchar(1000)
    layer: enum('I', 'II_III', 'IV', 'V', 'VI')
    -> CellCenters
    """


@schema
class NcdIterParams(dj.Lookup):
    definition = """
    param_id: smallint unsigned
    ---
    vasc_path: varchar(1000)
    -> Neuron
    num_threads: tinyint unsigned
    max_num_of_collisions: smallint unsigned
    main_axis: enum('x', 'y', 'z')
    pos_to_store: smallint unsigned
    bounds_checking: enum('true', 'false')
    """

@schema
class NcdIteration(dj.Computed):
    definition = """
    run_id: smallint unsigned
    -> NcdIterParams
    ---
    date = CURRENT_TIMESTAMP : timestamp
    result: longblob
    """

    def _make_tuples(self, key):
        pass


@schema
class AggRunParams(dj.Lookup):
    definition = """
    param_id: smallint unsigned
    ---
    max_collisions: smallint unsigned
    threshold: tinyint unsigned
    """


@schema
class AggRun(dj.Computed):
    definition = """
    run_id: smallint unsigned
    -> NcdIteration
    -> AggRunParams
    ---
    result: external-raw
    """


@schema
class CollisionsParse(dj.Computed):
    definition = """
    run_id: smallint unsigned
    -> AggRun
    ---
    result: external-raw
    """

# @schema
# class GraphNeuron(dj.Computed):
#     definition = """

