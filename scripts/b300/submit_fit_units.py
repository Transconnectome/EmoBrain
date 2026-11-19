#!/usr/bin/env python3
"""Render 48-hour-safe Slurm commands. Default dry-run; never submits a full sweep."""
import argparse
import json
import math
from pathlib import Path
import shlex
import subprocess
import sys


def conservative_bound(metrics,max_epochs=300,margin_fraction=.25,fixed_margin_s=600):
    durations=metrics['epoch_durations_s']
    if not durations or any(not math.isfinite(x) or x<=0 for x in durations):raise ValueError('actual epoch durations required')
    overhead=metrics['setup_before_fit_s']+metrics['post_fit_restore_predict_save_s']
    if overhead<0 or not math.isfinite(overhead):raise ValueError('invalid overhead')
    return (max(durations)*max_epochs+overhead)*(1+margin_fraction)+fixed_margin_s


def pack(bounds,limit_s=46*3600):
    if not bounds:raise ValueError('empty packing')
    groups=[];current=[];total=0
    for uid,bound in bounds.items():
        if not math.isfinite(bound) or bound<=0 or bound>=limit_s:raise ValueError(f'unit cannot safely fit: {uid}')
        if total+bound>=limit_s:groups.append(current);current=[];total=0
        current.append(uid);total+=bound
    if current:groups.append(current)
    return groups


def render(manifest,root,units,repo='/scratch/emobrain/code',time_limit='08:00:00'):
    h,m,s=map(int,time_limit.split(':'))
    if h*3600+m*60+s>46*3600:raise ValueError('operational limit is 46h, with 2h cap margin')
    cmd=['/scratch/envs/centaur/bin/python',repo+'/scripts/b300/fit_units.py','run','--manifest',manifest,'--root',root,'--units',','.join(units)]
    return '\n'.join(['#!/bin/bash','#SBATCH --job-name=emobrain-fit-units','#SBATCH --partition=gpu','#SBATCH --nodelist=b300-01','#SBATCH --ntasks=1','#SBATCH --gres=gpu:1','#SBATCH --cpus-per-task=8','#SBATCH --mem=96G',f'#SBATCH --time={time_limit}','set -euo pipefail',': "${SLURM_JOB_ID:?Slurm required}"','export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 CUBLAS_WORKSPACE_CONFIG=:4096:8',f'cd {shlex.quote(repo)}','exec '+shlex.join(cmd),''])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',required=True);p.add_argument('--root',required=True);p.add_argument('--units',required=True);p.add_argument('--output',required=True);p.add_argument('--time',default='08:00:00');a=p.parse_args()
    from fit_units import read_json,validate_manifest,unit_by_id
    m=validate_manifest(read_json(a.manifest));ids=a.units.split(',')
    for uid in ids:unit_by_id(m,uid)
    out=Path(a.output)
    with out.open('x') as f:f.write(render(a.manifest,a.root,ids,time_limit=a.time))
    print(json.dumps(dict(submitted=False,script=str(out),command=['sbatch','--parsable','--output',a.root+'/slurm_%j.log',str(out)])))

if __name__=='__main__':main()
