#!/bin/bash
#SBATCH -p spree
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 60
#SBATCH -t 20-00:00:00
#SBATCH -o slurm-log-%J.out
#SBATCH -x s1604-calc01

$1 --version
echo $SLURM_JOB_ID
$1 $2 > $3/execution_log.txt 2>&1

