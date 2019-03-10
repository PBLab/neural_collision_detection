import datajoint as dj


schema = dj.schema('ncd', locals())


@schema
class VasculatureData(dj.Manual):
    definition = """
    file_id: smallint unsigned
    ---
    fname: varchar(1000)
    """


@schema
class CellCenters(dj.Manual):
    definition = """
    file_id: smallint unsigned
    -> VasculatureData
    ---
    fname: varchar(1000)
    layer: enum('I', 'II', 'III', 'IV', 'V', 'VI')
    """


@schema
class Neuron(dj.Manual):
    definition = """
    neuron_id: smallint unsigned
    ---
    name: varchar(25)
    layer: enum('I', 'II', 'III', 'IV', 'V', 'VI')
    -> CellCenters
    """


@schema
class NcdIteration(dj.Computed):
    definition = """
    run_id: smallint unsigned
    ---
    date = CURRENT_TIMESTAMP : timestamp
    vasc_path: varchar(1000)
    -> Neuron
    output_path: varchar(1000)
    num_threads: tinyint unsigned
    max_num_of_collisions: smallint unsigned
    main_axis: enum('x', 'y', 'z')
    pos_to_store: smallint unsigned
    bounds_checking: enum('true', 'false')
    """


@schema
class AggRun(dj.Computed):
    definition = """
    run_id: smallint unsigned
    -> NcdIteration
    ---
    output_path: varchar(1000)
    max_collisions: smallint unsigned
    threshold: tinyint unsigned
    """


@schema
class CollisionsParse(dj.Computed):
    definition = """
    run_id: smallint unsigned
    -> AggRun
    ---
    output_path_npz: varchar(1000)
    output_path_mat: varchar(1000)
    """

# @schema
# class GraphNeuron(dj.Computed):
#     definition = """


if __name__ == "__main__":
    dj.conn()