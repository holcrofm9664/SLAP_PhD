#!/bin/bash
#SBATCH -J warehouse_optimisation
#SBATCH --mail-type=ALL
#SBATCH --mail-user=m.holcroft@lancaster.ac.uk
#SBATCH -c 25
#SBATCH --mem-per-cpu=3GB
#SBATCH -o ./output_scripts/mytestjob.out


# Activate virtual environment
source ~/start-pyenv
source ~/venvs/warehouse/bin/activate

mkdir -p logs

# export OMP_NUM_THREADS=1
# export MKL_NUM_THREADS=1
# export OPENBLAS_NUM_THREADS=1

# Tell python how many workers SLURM gave us

# export NUM_WORKERS=$SLURM_CPUS_PER_TASK

# Run the code

srun python run_parallel.py 24