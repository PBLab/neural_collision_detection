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
    -> VasculatureData
    -> Neuron
    num_threads: tinyint unsigned
    max_num_of_collisions: smallint unsigned
    main_axis: enum('x', 'y', 'z')
    pos_to_store: enum('true', 'false')
    bounds_checking: enum('true', 'false')
    results_folder: varchar(1000)
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

    def make(self, key):
        params = (NcdIterParams & key).fetch(as_dict=True)[0]
        ncd_path = '../ncd'
        vascular_data = (VasculatureData & {'vasc_id': params['vasc_id']}).fetch1('fname')
        neuron = Neuron & {'neuron_id': params['neuron_id']}
        neural_data = neuron.fetch1('fname')
        neuron_name = neuron.fetch1('name')
        threads_cnt = params['num_threads']
        centers = (CellCenters & {'centers_id': neuron.fetch1('centers_id')}).fetch1('fname')
        output_dir = params['results_folder']
        ncd_output_file = output_dir + f'/ncd_results_{neuron_name}'
        max_col_cnt = params['max_num_of_collisions']
        store_min_pos = '-z' if params['pos_to_store'] == 'true' else ''
        bounds_checking = '-b' if params['bounds_checking'] == 'true' else ''
        ncd_command = f"{ncd_path} -m batch -V {vascular_data} -N {neural_data} -t {threads_cnt} -i {centers} -o {output_dir} -f {ncd_output_file} -c {max_col_cnt} {store_min_pos} {bounds_checking}"
        print(ncd_command)


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

