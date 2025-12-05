#!/bin/bash

#SBATCH --job-name=download_data
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --time=0-150:00:00  # 시간 제한 (최대 36시간)
#SBATCH --mem=20GB
#SBATCH --partition=laal_a6000
#SBATCH --cpus-per-task=8
#SBATCH --output=/home/wnsdh/slurm_log/S-%x.%j.out

source ~/.bashrc
source /home/wnsdh/miniconda3/etc/profile.d/conda.sh
conda activate bkms2

streamlit run streamlit_model_selector_app.py

