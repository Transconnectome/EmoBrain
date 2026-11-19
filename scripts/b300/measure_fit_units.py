#!/usr/bin/env python3
"""Per-fit instrumentation. Driver samples are sampled observations, not exact peaks."""
from __future__ import annotations
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import threading
import time


def query(fields,kind='gpu'):
    cp=subprocess.run(['nvidia-smi',f'--query-{kind}={fields}','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5)
    if cp.returncode:raise RuntimeError(cp.stderr.strip())
    return [x.strip().split(', ') for x in cp.stdout.splitlines() if x.strip()]


class UnitTelemetry:
    def __init__(self,attempt,uid):
        self.path=Path(attempt);self.uid=uid;self.stop=threading.Event();self.samples=[];self.events=[];self.error=None
    def sample(self):
        row=dict(utc=time.time(),monotonic=time.monotonic())
        try:
            row['devices']=query('uuid,memory.used,utilization.gpu')
            row['processes']=query('gpu_uuid,pid,used_gpu_memory','compute-apps')
        except Exception as e:row['error']=repr(e)
        self.samples.append(row)
        with (self.path/'driver.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush()
    def loop(self):
        while not self.stop.wait(1):self.sample()
    def __enter__(self):
        import torch
        self.torch=torch;self.pid=os.getpid();self.started=time.monotonic();self.utc=time.time()
        self.sample()
        first=self.samples[0]
        if 'error' in first:raise RuntimeError('telemetry not ready: '+first['error'])
        devices=first['devices']
        if len(devices)!=1:raise ValueError(f'expected one allocation-visible GPU, got {len(devices)}')
        self.uuid=devices[0][0]
        self.ready=time.monotonic()
        self.thread=threading.Thread(target=self.loop,name='gpu-driver-sampler',daemon=False);self.thread.start()
        self.old_term=signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGTERM,self.interrupt)
        torch.cuda.synchronize();self.baseline=self.memory();torch.cuda.reset_peak_memory_stats()
        return self
    def interrupt(self,signum,frame):raise InterruptedError(f'Slurm signal {signum}')
    def memory(self):
        t=self.torch.cuda
        return dict(allocated=t.memory_allocated(),reserved=t.memory_reserved(),peak_allocated=t.max_memory_allocated(),peak_reserved=t.max_memory_reserved())
    def observe(self,event,payload):
        self.torch.cuda.synchronize();now=time.monotonic()
        row=dict(event=event,utc=time.time(),monotonic=now,payload=payload,memory=self.memory())
        if event=='fit_start':self.fit_start=now;self.last_epoch=now
        elif event=='epoch':row['epoch_duration_s']=now-self.last_epoch;self.last_epoch=now
        elif event=='fit_end':self.fit_end=now
        self.events.append(row)
        with (self.path/'epochs.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
        print('FIT_EVENT',self.uid,event,json.dumps(payload),flush=True)
    def __exit__(self,typ,value,tb):
        self.stop.set();self.thread.join(timeout=12)
        signal.signal(signal.SIGTERM,self.old_term)
        try:self.torch.cuda.synchronize();end_memory=self.memory()
        except Exception as e:end_memory={'error':repr(e)}
        self.sample();end=time.monotonic()
        good=[s for s in self.samples if 'error' not in s];gaps=[b['monotonic']-a['monotonic'] for a,b in zip(self.samples,self.samples[1:])]
        dev=[];proc=[]
        for s in good:
            for row in s['devices']:
                if row[0]==self.uuid:
                    try:dev.append(float(row[1]))
                    except ValueError:pass
            for row in s['processes']:
                if row[0]==self.uuid and row[1]==str(self.pid):
                    try:proc.append(float(row[2]))
                    except ValueError:pass
        report=dict(unit=self.uid,pid=self.pid,gpu_uuid=self.uuid,slurm_job_id=os.environ.get('SLURM_JOB_ID'),cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),start_utc=self.utc,end_utc=time.time(),wall_s=end-self.started,sampler_ready_monotonic=self.ready,fit_start_monotonic=getattr(self,'fit_start',None),baseline_bytes=self.baseline,end_bytes=end_memory,epoch_durations_s=[x['epoch_duration_s'] for x in self.events if x['event']=='epoch'],setup_before_fit_s=getattr(self,'fit_start',end)-self.started,post_fit_restore_predict_save_s=end-getattr(self,'fit_end',end),driver_device_sampled_peak_mib=max(dev) if dev else None,driver_process_sampled_peak_mib=max(proc) if proc else None,sample_count=len(self.samples),error_samples=len(self.samples)-len(good),max_sample_gap_s=max(gaps) if gaps else None,sampler_joined=not self.thread.is_alive(),max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,status='complete' if typ is None else 'interrupted_or_failed',exception=repr(value) if value else None,limits='Driver samples may miss peaks; setup/post-fit include multiple operations. RSS is process lifetime high-water mark. CUDA baseline includes resident dependencies.')
        from fit_units import publish_json
        publish_json(self.path/'telemetry.json',report)
        if self.thread.is_alive():raise RuntimeError('sampler did not terminate')
        return False
