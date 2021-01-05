u"""
Runnig multiple jobs with the same job command.

    This script grabs a list of files_names from a given directory (input_dir)
and inserts each file name into a job command. the job command is wrapped with
the bsub command along with it's specified options and run in bash.
    both the input directory, the job command and the bsub arguments can
be passed as arguments by the user.

    example:
    running a cutadapt command with new-all queue::
            $python run_bsub.py -q new-all.q -in fastq_files  -out trimmed_files
             -regex SOME_REGULAR_EXPRESSION 'cutadapt -a AGATCGGAAGAGCACAC
             -A AGATCGGAAGAGC --times 2 -q 30 -m 20
             -o $output_dir/$file1_trimmed.fastq -p $output_dir/$file2_trimmed.fastq
             $input_dir/$file1_001.fastq.gz $input_dir/$file2_001.fastq.gz'

        notice the quotes around the job command (cutadapt in this case),
    this is required for correct parsing. Also notice the dollar signs preceded by either file, input_dir or output_dir,
    these are reserved keywords that will be replaced by the job specific arguments passed under -in, -out and the match
    of the regular expression.
    The regular expression is designed to capture the unique sample file name
    and insert it in the appropriate location in the job command.

        Todo:
            * write the main loop as a function.
            * add a readable time stamp to err file names
            * document how the job command is passed
            * give more help on the argument parser (groups?)
"""
import pdb
import re
import subprocess
import argparse
import hashlib
from datetime import datetime

ENCODING = 'utf-8'

# --------------------------- parsing ---------------------
parser = argparse.ArgumentParser()
# # module argument
# parser.add_argument("module", choices=['basic', 'sam_to_bam'],
#                                         help='which module to run')
# job command args
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
    memory = ['-R', required_memory] if args.memory else None
else:
    memory = None

# job command variables
input_dir = args.input_dir if args.input_dir else None
output_dir = args.output_dir if args.output_dir else None
file_id_regex = args.regex
command = args.command

# patterns to be replcaed in the job command
file_pattern = r'\@file'
input_dir_pattern = r'\@input_dir'
output_dir_pattern = r'\@output_dir'

# --------------------------- get file names ----------------------------------
get_file_names = subprocess.Popen([f'ls -1 {input_dir}'],
                                  shell=True, stdout=subprocess.PIPE)
file_names = [byte.decode(ENCODING) for
              byte in get_file_names.stdout.read().splitlines()]

print('files:', file_names)
# --------------------------- run the command for each file --------------------
compiled_pattern = re.compile(rf'{file_id_regex}')
for i, file_name in enumerate(file_names):

    ## match pattern and return match
    match = compiled_pattern.match(file_name)
    file_id = match.group()

    # generate a job hash
    now = datetime.now()
    job_and_time = f'{file_id}.{now}'.encode()
    job_hash = hashlib.md5(job_and_time).hexdigest()

    # job name
    job_id = f'job.{job_hash}'

    # insert relevant input and output dir and file name into command
    pattern_replacement = [
        (file_pattern, file_id),
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
    if i == 0:
        print('this goes into run(): ' + command_to_run)
    subprocess.run(command_to_run, text=True, shell=True) # uncomment this when running in WEXAC







