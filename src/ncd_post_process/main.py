import os, sys, subprocess
import pathlib

import datajoint as dj
from datajoint_pipe.dj_tables import *
import attr
from attr.validators import instance_of

################################## PARAMS ##################################################

ROOT = "../.."
PYTHON_PATH = "/state/partition1/apps/python/anaconda2/bin/python"
VASCULAR_DATA_PATH = os.path.join(ROOT, "vascular/vascular.0.999.obj")
NEURAL_DATA_PATH = os.path.join(ROOT, "neurons/AP120410_s1c1.obj")
CENTERS_PATH = os.path.join(ROOT, "centers/centers_0.01.csv")
RUN_AGG_PATH = os.path.join(ROOT, "git/scripts/run_aggregator.py")
NCD_PATH = os.path.join(ROOT, "ncd")
RES_DIR = os.path.join(ROOT, "ncd_res")
THREADS_CNT = 24
MAX_COL_CNT = 400
MAX_COLLISIONS = 100
THRESHOLD_DISTANCE = 1

############################################################################################


def execute_pipeline(
    results_dir,
    vascular_data,
    neural_data,
    centers,
    max_collisions,
    threshold_distance,
    run_id,
):
    ncd_path = NCD_PATH
    threads_cnt = THREADS_CNT
    max_col_cnt = MAX_COL_CNT
    output_dir = os.path.join(results_dir, "dummy")
    ncd_output_file = os.path.join(results_dir, run_id + ".txt")

    ncd_command = "{ncd_path} -m batch -V {vascular_data} -N {neural_data} -t {threads_cnt} -i {centers} -o {output_dir} -f {ncd_output_file} -c {max_col_cnt} -z".format(
        **locals()
    )
    print("Running: " + ncd_command)
    subprocess.run(ncd_command.split())

    # print("Usage: %s <ncd output file> <max collisions> <threshold distance> <output file>" % argv[0])
    agg_db = os.path.join(results_dir, run_id + "_agg_db.csv")
    run_agg_path = RUN_AGG_PATH
    python_path = PYTHON_PATH
    run_aggregator_commnd = "{python_path} {run_agg_path} {ncd_output_file} {max_collisions} {threshold_distance} {agg_db}".format(
        **locals()
    )
    print("Running: " + run_aggregator_commnd)
    subprocess.run(run_aggregator_commnd.split())
    print("Done!")


def main(argv):
    if len(argv) < 2:
        print("Usage: %s <run id>" % argv[0])
        return 1

    run_id = argv[1]
    execute_pipeline(
        RES_DIR,
        VASCULAR_DATA_PATH,
        NEURAL_DATA_PATH,
        CENTERS_PATH,
        MAX_COLLISIONS,
        THRESHOLD_DISTANCE,
        run_id,
    )


@attr.s
class PipeRunner:
    num_threads = attr.ib(default=24, validator=instance_of(int))
    max_num_of_collisions = attr.ib(default=500, validator=instance_of(int))
    main_axis = attr.ib(default="z", validator=instance_of(str))
    pos_to_store = attr.ib(default=True, validator=instance_of(bool))
    bounds_checking = attr.ib(default=False, validator=instance_of(bool))
    results_folder = attr.ib(
        default=pathlib.Path(__file__).resolve().parents[2] / "results",
        validator=instance_of(pathlib.Path),
    )
    params = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.pos_to_store = "true" if self.pos_to_store else "false"
        self.bounds_checking = "true" if self.bounds_checking else "false"
        assert self.results_folder.exists()

    def run(self):
        # ncd_params = NcdIterParams()
        # agg_params = AggRunParams()
        # self._insert_ncd_params(ncd_params)
        # self._insert_agg_params(agg_params)
        pass

    def _insert_ncd_params(self, ncd_params: NcdIterParams):
        """
		Adds an entry to the NCDParams table with the current parameters.
		"""
        next_idx = len(ncd_params)
        cur_params = (
            next_idx,
            0,
            9,
            self.num_threads,
            self.max_num_of_collisions,
            self.main_axis,
            self.pos_to_store,
            self.bounds_checking,
            str(self.results_folder),
        )
        ncd_params.insert1(cur_params)

    def _insert_agg_params(self, agg_params):
        next_idx = len(agg_params)
        cur_params = (
            next_idx,

        )

    def _run_ncd(self, params):
        """
        Runs NCD based on parameters in params
        """
        ncd_iter = NcdIteration()
        key = len(ncd_iter)
        ncd_iter.populate()


if __name__ == "__main__":
    params = PipeRunner().run()
    ag = AggRun()
    ag.populate()
    # ic = NcdIteration()
    # ic.populate()
