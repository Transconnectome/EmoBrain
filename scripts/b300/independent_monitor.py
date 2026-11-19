#!/usr/bin/env python3
"""Project-only independent B300 ledger adapter; never submits or notifies.

register --jobs-file accepts new Slurm work units (id, name, stage, target|null,
unit, probe={slurm_job_id,log_path,step_regex}). record --updates-file updates
existing units; completed requires evidence={path,sha256} of a local receipt.
A scheduler COMPLETED state alone becomes awaiting_verification, not completion.
All mutations use the existing sibling .lock and atomic replacement.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess
import time

LIB = Path.home()/'.agents/skills/long-job-monitor/scripts/job_ledger.py'
spec = importlib.util.spec_from_file_location('shared_job_ledger', LIB)
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)
RUN = 'emobrain-core-v2'
STAGES = ('canonical_integration', 'roi_scientific_disposition', 'd3_d4_measurement',
          'partition_48h_restart', 'main_launch_preparation')


def validate_number(value, positive=False):
    if value is not None and (isinstance(value, bool) or not isinstance(value, (int,float))
                             or not math.isfinite(value) or value < 0 or (positive and value == 0)):
        raise ValueError('expected finite nonnegative number, positive target, or null')


def evidence_ok(evidence):
    if not isinstance(evidence, dict):
        raise ValueError('completed requires evidence={path,sha256}')
    p = Path(evidence['path'])
    if not p.is_absolute() or hashlib.sha256(p.read_bytes()).hexdigest() != evidence['sha256']:
        raise ValueError('receipt evidence hash mismatch')


def refresh(ledger, now):
    L.recompute_summary(ledger, now, observed=False)
    active = [j for j in ledger['jobs'] if j['status'] not in L.TERMINAL_STATUSES]
    warning = any(j.get('error') or j.get('warnings') for j in active) or ledger.get('host_observation', {}).get('cache_fresh') is False
    startup = ledger.get('tick_count', 0) < 2 or any(
        j.get('status_since') is not None and 0 <= now-j['status_since'] < 1800
        for j in active if j.get('kind') == 'work_unit')
    interval = 0 if not active else (900 if warning or startup else 1800)
    ledger.update(active=bool(active), next_interval_sec=interval,
                  next_check_epoch=now+interval if interval else None,
                  phase='terminal' if not active else ('warning' if warning else 'independent_b300'),
                  next_interval_reason='15m startup/anomaly; otherwise 30m; plan units are not submitted jobs')


def mutate(path, command, payload=None, live_state=None):
    with L.locked_ledger(path):
        ledger = L.read_json(path)
        if ledger.get('monitor_schema') != 'independent-b300-v1':
            raise ValueError('not a migrated independent B300 ledger')
        now = time.time()
        by_id = {j['id']:j for j in ledger['jobs']}
        if command == 'register':
            incoming = set()
            for raw in payload:
                jid = raw['id']
                if not re.fullmatch(r'[A-Za-z0-9_.-]+',jid) or jid in by_id or jid in incoming:
                    raise ValueError('duplicate or unsafe work-unit id')
                incoming.add(jid)
                p = raw.get('probe', {})
                if not re.fullmatch(r'[0-9]+(?:_[0-9]+)?',str(p.get('slurm_job_id',''))):
                    raise ValueError('actual Slurm job id required')
                if not str(p.get('log_path','')).startswith('/scratch/emobrain/') or not p.get('step_regex'):
                    raise ValueError('exact /scratch/emobrain log and progress regex required')
                re.compile(p['step_regex'])
                validate_number(raw.get('target'), True)
                job = L.normalize_job_spec({**raw,'host':'b300-01','status':'pending',
                    'probe':{**p,'kind':'slurm','host':'b300-01'}})
                job['kind']='work_unit'; job['status_since']=now
                ledger['jobs'].append(job)
        elif command == 'record':
            for update in payload:
                if update['id'] not in by_id:
                    raise KeyError(update['id'])
                if by_id[update['id']].get('kind') == 'historical_pilot':
                    raise ValueError('historical pilot is immutable')
                if update.get('status',by_id[update['id']]['status']) not in {
                    'planned','pending','running','awaiting_verification','completed','failed','cancelled'}:
                    raise ValueError('unsupported status')
                for key in ('current','target','gpu_util','log_age_sec'):
                    if key in update: validate_number(update[key],key=='target')
                if update.get('status') == 'completed': evidence_ok(update.get('evidence'))
            L.apply_updates(ledger,payload,now)
            for update in payload:
                if 'target' in update: by_id[update['id']]['target']=update['target']
                if 'evidence' in update: by_id[update['id']]['evidence']=update['evidence']
        elif command == 'tick':
            if ledger.get('tick_count', 0) >= 2 and now < ledger.get('next_check_epoch', 0):
                return ledger
            # Fetch cache before any SSH; planning-only ticks never open SSH.
            state = live_state if live_state is not None else L._fetch_b300_live()
            age = now-state.get('collected_at',0) if L._is_num(state.get('collected_at')) else None
            ledger['host_observation']={'at':now,'cache_age_sec':age,
                'cache_fresh':age is not None and 0 <= age <= 300,
                'error':state.get('_error'), 'source':'b300-live'}
            jobs = [j for j in ledger['jobs'] if j.get('kind')=='work_unit'
                    and j['status'] not in L.TERMINAL_STATUSES]
            if jobs:
                if live_state is not None:
                    raise ValueError('fixture tick forbids remote work units')
                master = subprocess.run(['ssh','-O','check','b300-01'],capture_output=True,text=True,timeout=10)
                if master.returncode:
                    updates=[{'id':j['id'],'error':'B300 SSH master unavailable; skipped'} for j in jobs]
                else:
                    updates=L._probe_remote_slurm_batch('b300-01',jobs,b300_state=state)
                for upd in updates:
                    if upd.get('status')=='completed':
                        upd['status']='awaiting_verification'
                        upd['note']='Slurm completed; artifact verification receipt required'
                L.apply_updates(ledger,updates,now)
            else:
                ledger['tick_count']=ledger.get('tick_count',0)+1
            ledger['last_health_tick']=now
        else:
            raise ValueError(command)
        ledger['updated_at']=now
        refresh(ledger,now)
        L.write_json_atomic(path,ledger)
        return ledger


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--state-dir',type=Path,default=L.DEFAULT_STATE_DIR)
    sub=ap.add_subparsers(dest='command',required=True)
    sub.add_parser('status')
    tick=sub.add_parser('tick'); tick.add_argument('--fixture-live',type=Path)
    reg=sub.add_parser('register'); reg.add_argument('--jobs-file',type=Path,required=True)
    rec=sub.add_parser('record'); rec.add_argument('--updates-file',type=Path,required=True)
    args=ap.parse_args(); path=L.ledger_path_for(RUN,args.state_dir)
    L.set_process_name('emobrain-mon')
    if args.command=='status': result=L.read_json(path)
    else:
        payload_path=getattr(args,'jobs_file',None) or getattr(args,'updates_file',None)
        payload=json.loads(payload_path.read_text()) if payload_path else None
        fixture=getattr(args,'fixture_live',None)
        if fixture and args.state_dir.resolve()==L.DEFAULT_STATE_DIR.resolve():
            ap.error('fixtures require isolated --state-dir')
        result=mutate(path,args.command,payload,json.loads(fixture.read_text()) if fixture else None)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
