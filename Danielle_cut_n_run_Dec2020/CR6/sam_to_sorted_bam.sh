#TODO load samtools module when script begins
#TODO allow <SIZE_TO_FILTER_BY> as a user argument
#TODO unique job name for each job/commmand
#TODO bsub err and out files. maybe name them with unique job name as well as sample name
#TODO add a simple debugger for regex. maybe for first iteration print regex and the match if there was one
#!bin/bash

# @@@--- pass named arguments ---------------------------------- @@@
# usage example: bash run_bsub.sh <input_dir> <output_dir> QUEUE=<queue_name>
# this doesnt allow spaces in named argument
#for ARGUMENT in ${@:3}
#do
#
#     KEY=$(echo $ARGUMENT | cut -f1 -d=)
#     VALUE=$(echo $ARGUMENT | cut -f2 -d=)   
#
#     case "$KEY" in
#            QUEUE)              QUEUE=${VALUE} ;;
#            *)   
#     esac    
#
#done

# @@@--- initialize constants ---------------------------------- @@@
input_dir=$1
output_dir=$2

# @@@--- main loop --------------------------------------------- @@@
regex=[A-Za-z0-9]+
for file in `ls -1 $input_dir`; do
   
    echo file being processed: $file
    
    # @@@-- capture sample name -------------------------------- @@@
    if [[ $file =~ $regex ]];
    then
        echo "sample_name: ${BASH_REMATCH[0]}"
        sample_name=${BASH_REMATCH[0]}
    else
        echo "$file didn't match $regex!"
    fi
    
    # @@@-- intialize local constants --------------------------- @@@
    #err_path='./err/${sample_name}.err'
    #out_path='./out/${sample_name}.out'
    input_sam_path=${input_dir}/${sample_name}.sam 
    filtered_sam_path=${output_dir}/${sample_name}_temp.sam
    temp_bam_path=${output_dir}/${sample_name}_temp.bam
    output_bam_path=${output_dir}/${sample_name}.bam

    # @@@-- write header ------------------------------------------------- @@@
    command_write_header="samtools view -H ${input_sam_path} >> ${filtered_sam_path}"
    bsub -J "write_header" -q new-all.q -e ${output_dir}/${sample_name}.err -o ${output_dir}/${sample_name}.out "${command_write_header}"
    
    # @@@-- filter out unmapped, discordant and size irrelevant alignments @@@
    command_filter="samtools view -F 4 -f 0x2 ${input_sam_path} >> ${filtered_sam_path}" 
    bsub -w "done(write_header)" -J "filter" -q new-all.q -R "rusage[mem=4240]" -e ${output_dir}/${sample_name}.err -o ${output_dir}/${sample_name}.out "${command_filter}" 
    
    # @@@-- convert to bam ----------------------------------------------- @@@
    command_convert="samtools view -b ${filtered_sam_path} >> ${temp_bam_path}"
    bsub -w "done(filter)" -J "convert" -q new-all.q -e ${output_dir}/${sample_name}.err -o ${output_dir}/${sample_name}.out "${command_convert}" 

    # @@@-- sort  -------------------------------------------------------- @@@
    command_sort="samtools sort -o ${output_bam_path} ${temp_bam_path}"
    bsub -w "done(convert)" -J "sort" -q new-all.q -e ${output_dir}/${sample_name}.err -o ${output_dir}/${sample_name}.out ${command_sort} 

    # @@@-- index -------------------------------------------------------- @@@
 #   command_index="samtools index ${output_bam_path}"
 #   bsub -w "done(sort)" -J "index" -q new-all.q -e ${output_dir}/${sample_name}.err -o ${output_dir}/${sample_name}.out ${command_index}

done

#  samtools view -H mapping/sam_files/CR13EZh2_S1.sam >> mapping/headers/CR13EZh2_S1_temp.sam 
#  samtools view -F 4 -f 0x2 mapping/sam_files/CR13EZh2_S1.sam | awk -F '\t' '{if ($9 > 120) print $0}' >> mapping/headers/CR13EZh2_S1_temp.sam




#TODO allow bsub options to be passed as command line args 
#TODO eventualy write this script so that it can take both bsub options and a Job command as arguments. preferably named args 
#TODO a number of bsub Jobs are being submitted one after the other. is that desirable?
    # this was solved by naming jobs and adding a **-w "done(<previous job name>)"** to any job that has dependencies
