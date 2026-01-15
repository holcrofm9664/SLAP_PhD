#!/bin/bash
#SBATCH --job-name=full_warehouse_optimisation
#SBATCH --cpus-per-task=24
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

# Load required modules

module load python
module load gurobi

# Activate virtual environment

source ~/venvs/warehouse/bin/activate

mkdir -p logs

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

# Tell python how many workers SLURM gave us

export NUM_WORKERS=$SLURM_CPUS_PER_TASK

# Run the code

python run_parallel.py