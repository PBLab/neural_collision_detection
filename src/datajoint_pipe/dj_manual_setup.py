"""
This script was run only once, and populated all
of the needed manual entries in the database. In case
we delete some table it should be run again.
"""
import importlib
import pathlib
import itertools
import datetime

from dj_tables import *


def drop_all():
    """
    Removes all manual tables
    """
    CollisionsParse().drop_quick()
    AggRun().drop_quick()
    AggRunParams().drop_quick()
    NcdIteration().drop_quick()
    NcdIterParams().drop_quick()
    Neuron().drop_quick()
    CellCenters().drop_quick()
    VasculatureData().drop_quick()


def populate_vasc():
    vasc = VasculatureData()
    vasc.insert1(
        (
            0,
            "/data/neural_collision_detection/data/vascular/vascular.obj",
            "/data/neural_collision_detection/data/vascular/vascular_balls.csv",
        )
    )


def populate_cell_centers():
    cells = CellCenters()
    cells.insert1(
        (
            0,
            0,
            "/data/neural_collision_detection/data/vascular/centers_layer_ONE.csv",
            "I",
        )
    )
    cells.insert1(
        (
            1,
            0,
            "/data/neural_collision_detection/data/vascular/centers_layer_TWOTHREE.csv",
            "II_III",
        )
    )
    cells.insert1(
        (
            2,
            0,
            "/data/neural_collision_detection/data/vascular/centers_layer_FOUR.csv",
            "IV",
        )
    )
    cells.insert1(
        (
            3,
            0,
            "/data/neural_collision_detection/data/vascular/centers_layer_FIVE.csv",
            "V",
        )
    )
    cells.insert1(
        (
            4,
            0,
            "/data/neural_collision_detection/data/vascular/centers_layer_SIX.csv",
            "VI",
        )
    )


def populate_neurons():
    neuron = Neuron()
    neuron_names = [
        "AP120410_s1c1",
        "AP120410_s3c1",
        "AP120412_s3c2",
        "AP120416_s3c1",
        "AP120419_s1c1",
        "AP120420_s1c1",
        "AP120420_s2c1",
        "AP120507_s3c1",
        "AP120510_s1c1",
        "AP120522_s3c1",
        "AP120524_s2c1",
        "AP120614_s1c2",
        "AP130312_s1c1",
        "AP131105_s1c1",
    ]
    layers = [
        ("V", 3),
        ("V", 3),
        ("V", 3),
        ("IV", 2),
        ("VI", 4),
        ("IV", 2),
        ("II_III", 1),
        ("II_III", 1),
        ("II_III", 1),
        ("I", 0),
        ("II_III", 1),
        ("V", 3),
        ("II_III", 2),
        ("II_III", 2),
    ]
    assert len(neuron_names) == len(layers)
    for idx, (neuron_name, layer) in enumerate(zip(neuron_names, layers)):
        fname = f"/data/neural_collision_detection/data/neurons/{neuron_name}.xml"
        neuron.insert1((idx, neuron_name, fname, layer[0], layer[1], 0))


def populate_agg_params(only_one: bool = False):
    agg_params = AggRunParams()
    collisions = (0, 10, 20, 50, 100, 200)
    threshold = range(10)
    for idx, (coll, thresh) in enumerate(itertools.product(collisions, threshold)):
        agg_params.insert1((idx, coll, thresh))
        if only_one:
            break


def populate_ncd_params(only_one: bool = False):
    ncd_params = NcdIterParams()
    vasc_id = 0
    neuron_ids = range(14)
    num_threads = 24
    max_coll_num = (0, 10, 20, 50, 100, 200)
    main_axis = "z"
    pos_to_store = "true"
    bounds_checking = "false"
    results_folder_base = str(pathlib.Path(__file__).resolve().parents[2] / "results" / str(datetime.datetime.now().date()) / 'id_{}')
    if only_one:
        for idx, cur_max_coll_num in enumerate(max_coll_num):
            results_folder = pathlib.Path(results_folder_base.format(idx))
            results_folder.mkdir(parents=True, exist_ok=True)
            results_folder = str(results_folder)
            ncd_params.insert1(
                (
                    idx,
                    vasc_id,
                    3,
                    num_threads,
                    cur_max_coll_num,
                    main_axis,
                    pos_to_store,
                    bounds_checking,
                    results_folder,
                )
            )

        return

    for idx, neuron in enumerate(neuron_ids):
        ncd_params.insert1(
            (
                idx,
                vasc_id,
                neuron,
                num_threads,
                max_coll_num,
                main_axis,
                pos_to_store,
                bounds_checking,
                results_folder.format(idx),
            )
        )


if __name__ == "__main__":
    drop_all()
    import dj_tables

    dj_tables = importlib.reload(dj_tables)
    populate_vasc()
    populate_cell_centers()
    populate_neurons()
    populate_agg_params(False)
    populate_ncd_params(True)
