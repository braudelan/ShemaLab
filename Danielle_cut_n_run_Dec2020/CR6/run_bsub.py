#!/usr/bin/python3
import pdb
import re
import subprocess
import argparse
import hashlib
from datetime import datetime
#from num2words import num2words

ENCODING = 'utf-8'

# --------------------------- parsing ---------------------
parser = argparse.ArgumentParser()
# # module argument
# parser.add_argument("module", choices=['basic', 'sam_to_bam'],
#                                         help='which module to run')

# debug
parser.add_argument('-d', '--debug', action='store_true', default=None)

# job command args
parser.add_argument('-f', '--input_files', action='append', default=None)
parser.add_argument('-in', '--input_dir', default=None,
                    help='directory to look for files to be processed')
parser.add_argument('-out', '--output_dir', default=None,
                    help='directory where processed files are saved' )
parser.add_argument('-regex', default=None,
                    help='the match will be substituted into command')
parser.add_argument(
    '-c',
    '--command',
    default=None,
    help='the command to be executed by bsub. '\
         'a literal @file will be replaced by regex match, '\
         'a literal @input_dir will be replaced by input_dir, '\
         'a literal @output_dir will be replaced by output_dir.'
)
# bsub args
parser.add_argument('-q', '--queue', type=str, required=True)
parser.add_argument('-m', '--memory', type=int, default=None,
                                        help='requested memory in MB')

# parse
args = parser.parse_args()

# --------------------------- initializing variables ----------------------
# bsub options
queue = ['-q', args.queue]
if args.memory:
    required_memory = f'rusage[mem={args.memory*1024}]' # convert KB to MB
    memory = ['-R', f'"{required_memory}"'] if args.memory else None
else:
    memory = None

# job command variables
input_dir = args.input_dir if args.input_dir else None
output_dir = args.output_dir if args.output_dir else None
sample_id_regex = args.regex
command = args.command

# patterns to be replcaed in the job command
sample_pattern = r'\@sample'
input_dir_pattern = r'\@input_dir'
output_dir_pattern = r'\@output_dir'

# --------------------------- get file names ----------------------------------
# if input files are given explicitly assign them to the file_names variable,
# otherwise, get
if args.input_files:
    file_names = args.input_files
else:
    get_file_names = subprocess.Popen([f'ls -1 {input_dir}'],
                                  shell=True, stdout=subprocess.PIPE)
    file_names = [byte.decode(ENCODING) for
                    byte in get_file_names.stdout.read().splitlines()]
print(f'\nthese are the file names: {file_names}\n\n')

# --------------------------- build a list of samples from file names ----------
sample_names = []
compiled_pattern = re.compile(rf'{sample_id_regex}')
for i, file_name in enumerate(file_names):

    ## match pattern and return match
    match = compiled_pattern.match(file_name)
    sample_id = match.group()
    sample_names.append(sample_id)
#nput_dir}/${sample_name}.sam
unique_sample_names = list(set(sample_names))

# ---------------------- print some of the parameters --------------------
print(
    f'\n@@@@@@@@@@@@  run_bsub.py parameters  @@@@@@@@@@@@@@@@@@@@@\n'
    f'\ninput directory: {input_dir}\n'
    f'output directory: {output_dir}\n'
    f'unique sample names: {unique_sample_names}\n'
    f'number of unique sample names: {len(unique_sample_names)}\n\n'
    f'\n@@@@@@@@@@@@@@  jobs  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n'
)


# ---------------------- run the command for each sample --------------------
for i, sample_name in enumerate(unique_sample_names):
    # generate a job hash
    now = datetime.now()
    job_and_time = f'{sample_name}.{now}'.encode()
    job_hash = hashlib.md5(job_and_time).hexdigest()

    # job name
    job_id = f'job.{job_hash[:10]}'

    # insert relevant input and output dir and sample name into command
    pattern_replacement = [
        (sample_pattern, sample_name),
        (input_dir_pattern, input_dir),
        (output_dir_pattern, output_dir)
    ]
    job_command = command
    for pattern, replacement in pattern_replacement:
        job_command = re.sub(pattern, replacement, job_command)
    job_command = f"\"{job_command}\""

    # build the paths and commands for bsub's output\
    # and error files
    bsub_error_path = ['-e', f'err/{job_id}']
    bsub_output_path = ['-o', f'out/{job_id}']

    options_for_command = [
        'bsub',
        queue,
        memory,
        bsub_error_path,
        bsub_output_path,
        job_command,
    ]

    commands_to_run = []
    for variable in options_for_command:
        if variable and type(variable) != list:
            commands_to_run.append(variable)
        elif variable and type(variable) == list:
            commands_to_run.extend(variable)
        else:
            continue

    # run the complete command in bash
    command_to_run = " ".join(commands_to_run)
#    print(num2words(i + 1, to='ordinal_num') + ' job')
    print('--------------------------------\n')
    print(f'sample name: {sample_name}\n')
    print(f'job command:\n{command_to_run}\n')

    if not args.debug:
        subprocess.run(command_to_run, text=True, shell=True)
