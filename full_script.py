# This script produces a log file for a workload. This workload is generated based on the parameters in all caps at the top of the file.
# To run, call like "python full_script.py <log base name> | ts -s '[%H:%M:%.S]' | tee <report log name>
# The pipes allow you to add timestamps to each print statement and to ensure it lands in a file
# This script generates a LOT of files. It is strongly recommended to have your <log base name> in a dedicated folder
from multiprocessing.pool import ThreadPool
from random import choice
from subprocess import check_call, check_output, STDOUT
from sys import argv, stdout


def generate_run(base_port, logname):
    check_call(['python', 'script_template.py', str(base_port), logname])
    check_call(['python', 'log_bucketizer.py', logname])
    check_call(['python', 'shuffler.py', logname])


def main():
    awaiting = []
    with ThreadPool() as p:
        base_port = choice(range(30000, 60001, 1000))
        for i in range(1, 21):
            logname = f'{argv[-1].rstrip(".log")}.run{i:02}.log'
            print(f"Starting generation for run {i}...")
            stdout.flush()
            awaiting.append(p.apply_async(generate_run, args=(base_port + i * 100, logname,)))
        for i, result in enumerate(awaiting):
            result.get()
            print(f"Generation for run {i} done!")
            stdout.flush()
    for i in range(1, 21):
        logname = f'{argv[-1].rstrip(".log")}.run{i:02}.log'
        print(f"Grading run {i}...")
        stdout.flush()
        print(check_output(['time', '-v', 'python', 'hlc_orderer.py', logname + '.shuffled'], stderr=STDOUT).decode())
        stdout.flush()
        print(check_output(['python', 'accuracy_grader.py', logname + '.bucketized', logname + '.shuffled.hlc_ordered']).decode())
        stdout.flush()
        print(check_output(['time', '-v', 'python', 'vc_orderer.py', logname + '.shuffled'], stderr=STDOUT).decode())
        stdout.flush()
        print(check_output(['python', 'accuracy_grader.py', logname + '.bucketized', logname + '.shuffled.vc_ordered']).decode())
        stdout.flush()


if __name__ == '__main__':
    main()