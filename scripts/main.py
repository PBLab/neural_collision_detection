import os, sys, subprocess

################################## PARAMS ##################################################

ROOT = "../.."
PYTHON_PATH = 			"/state/partition1/apps/python/anaconda2/bin/python"
VASCULAR_DATA_PATH = 	os.path.join(ROOT, "vascular/vascular.0.999.obj")
NEURAL_DATA_PATH = 		os.path.join(ROOT, "neurons/AP120410_s1c1.obj")
CENTERS_PATH = 			os.path.join(ROOT, "centers/centers_0.01.csv")
RUN_AGG_PATH =			os.path.join(ROOT, "git/scripts/run_aggregator.py")
NCD_PATH = 				os.path.join(ROOT, "ncd")
RES_DIR = 				os.path.join(ROOT, "ncd_res")
THREADS_CNT = 			24
MAX_COL_CNT = 			400
MAX_COLLISIONS = 		100
THRESHOLD_DISTANCE = 	1

############################################################################################

def execute_pipeline(results_dir, vascular_data, neural_data, centers, max_collisions, threshold_distance, run_id):
	ncd_path = NCD_PATH
	threads_cnt = THREADS_CNT
	max_col_cnt = MAX_COL_CNT
	output_dir = os.path.join(results_dir, "dummy")
	ncd_output_file = os.path.join(results_dir, run_id + ".txt")

	ncd_command = "{ncd_path} -m batch -V {vascular_data} -N {neural_data} -t {threads_cnt} -i {centers} -o {output_dir} -f {ncd_output_file} -c {max_col_cnt} -z".format(**locals())
	print ("Running: " + ncd_command)
	subprocess.check_output(ncd_command.split())

	#print("Usage: %s <ncd output file> <max collisions> <threshold distance> <output file>" % argv[0])
	agg_db = os.path.join(results_dir, run_id + "_agg_db.csv")
	run_agg_path = RUN_AGG_PATH
	python_path = PYTHON_PATH
	run_aggregator_commnd = "{python_path} {run_agg_path} {ncd_output_file} {max_collisions} {threshold_distance} {agg_db}".format(**locals())
	print ("Running: " + run_aggregator_commnd)
	subprocess.check_output(run_aggregator_commnd.split())
	print ("Done!")


def main(argv):
	if len(argv) < 2:
		print ("Usage: %s <run id>" % argv[0])
		return 1

	run_id = argv[1]
	execute_pipeline(RES_DIR, VASCULAR_DATA_PATH, NEURAL_DATA_PATH, CENTERS_PATH, MAX_COLLISIONS, THRESHOLD_DISTANCE, run_id)

if __name__ == "__main__":
	main(sys.argv)
