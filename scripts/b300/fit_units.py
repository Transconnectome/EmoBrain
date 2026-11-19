#!/usr/bin/env python3
"""Atomic S6 fit units. CPU validation is read-only; GPU execution requires Slurm.

Interrupted fits restart from their seed. Complete receipts are immutable and
content checked; a source done.json alone is never sufficient for reuse.
"""
from __future__ import annotations
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time
import uuid

REPO = Path(__file__).resolve().parents[2]
SCHEMA = 'emobrain-fit-units-v1'


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()


def identity(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def publish_json(path, value):
    """Publish once by hard link; never overwrite even under racing writers."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.parent/(path.name+'.tmp-'+uuid.uuid4().hex)
    with temp.open('x') as f:
        json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    try:os.link(temp,path)
    finally:temp.unlink()
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def safe_rel(value):
    p=Path(value)
    if p.is_absolute() or '..' in p.parts or not p.parts:raise ValueError('unsafe relative path')
    return p


def hash_tree(root):
    root=Path(root)
    if not root.is_dir():raise ValueError(f'missing artifact directory: {root}')
    out={}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():raise ValueError(f'symlink artifact: {p}')
        if p.is_file():out[str(p.relative_to(root))]=digest(p)
    if not out:raise ValueError('empty artifact tree')
    return out


def verify_hashes(root, hashes):
    if not hashes:raise ValueError('empty hash binding')
    for rel,sha in hashes.items():
        p=Path(root)/safe_rel(rel)
        if p.is_symlink() or not p.is_file() or digest(p)!=sha:raise ValueError(f'artifact changed or missing: {p}')


def validate_manifest(m):
    if m.get('schema')!=SCHEMA or m.get('restart_policy')!='restart_from_seed':raise ValueError('unsupported manifest/policy')
    units=m['units'];ids=[u['id'] for u in units]
    if not ids or len(ids)!=len(set(ids)) or sorted(ids)!=sorted(m['expected_units']):raise ValueError('declared unit universe mismatch')
    seen=set();paths=set()
    for u in units:
        if not u['id'] or '/' in u['id']:raise ValueError('invalid unit id')
        rel=str(safe_rel(u['artifact_rel']))
        if rel in paths:raise ValueError('two writers own one artifact path')
        paths.add(rel)
        if len(u['dependencies'])!=len(set(u['dependencies'])):raise ValueError('duplicate dependency')
        if not set(u['dependencies'])<=seen:raise ValueError('dependencies missing, cyclic or not topologically ordered')
        if not u['required'] or any(not safe_rel(x) for x in u['required']):raise ValueError('empty required contract')
        seen.add(u['id'])
    groups=m['groups'];gids=[g['id'] for g in groups]
    if len(gids)!=len(set(gids)):raise ValueError('duplicate group')
    for g in groups:
        if not g['units'] or len(g['units'])!=len(set(g['units'])) or not set(g['units'])<=seen:raise ValueError('group universe mismatch')
    if 'candidate_universe' in m:
        for condition,cands in m['candidate_universe'].items():
            folds=m['held_folds'] if condition in m['paired_conditions'] else [None]
            expected={(identity(c),j) for c in cands for j in folds}
            actual=[(identity(u['candidate']),u.get('held_fold')) for u in units if u['condition']==condition and not u['id'].startswith('inner')]
            if len(actual)!=len(expected) or set(actual)!=expected:raise ValueError('candidate/pair universe incomplete')
            group=next((g for g in groups if g['id']==condition),None)
            expected_ids={u['id'] for u in units if u['condition']==condition and not u['id'].startswith('inner')}
            if group is None or set(group['units'])!=expected_ids:raise ValueError('selection group excludes declared candidates')
        inners=[u['held_fold'] for u in units if u['id'].startswith('inner')]
        if sorted(inners)!=sorted(m['held_folds']):raise ValueError('inner universe incomplete')
    return m


def unit_by_id(m, uid):
    matches=[u for u in m['units'] if u['id']==uid]
    if len(matches)!=1:raise ValueError(f'unknown unit {uid}')
    return matches[0]


def receipt_path(root, uid):return Path(root)/'receipts'/f'{uid}.json'


def verify_unit(m, uid, root, checked=None):
    checked={} if checked is None else checked
    if uid in checked:return checked[uid]
    u=unit_by_id(m,uid);p=receipt_path(root,uid)
    if not p.is_file():raise ValueError(f'incomplete unit: {uid}')
    return verify_receipt(m,uid,root,read_json(p),checked)


def verify_receipt(m,uid,root,r,checked=None):
    """Validate candidate receipt before its one-time publication as complete."""
    checked={} if checked is None else checked
    u=unit_by_id(m,uid)
    if r['manifest_sha256']!=identity(m) or r['unit']!=u or r['status']!='complete':raise ValueError(f'stale receipt: {uid}')
    for dep in u['dependencies']:
        dr=verify_unit(m,dep,root,checked)
        if dr['run_key']!=r['run_key']:raise ValueError('dependency belongs to a different scientific run')
        if r['dependencies'].get(dep)!=digest(receipt_path(root,dep)):raise ValueError(f'dependency receipt changed: {dep}')
    folder=Path(root)/'science'/safe_rel(u['artifact_rel'])
    verify_hashes(folder,r['artifacts'])
    if hash_tree(folder)!=r['artifacts']:raise ValueError('unexpected artifact set')
    if not set(u['required'])<=set(r['artifacts']):raise ValueError('missing required artifact')
    done=read_json(folder/'done.json')
    if done['run_key']!=r['run_key'] or done['candidate']!=u['candidate'] or done['seed']!=u['seed']:raise ValueError('scientific identity mismatch')
    if 'held_fold' in u and done.get('held_fold')!=u['held_fold']:raise ValueError('held fold mismatch')
    expected_condition='feature_encoder_oof' if uid.startswith('inner') else u['condition']
    if done.get('condition')!=expected_condition:raise ValueError('scientific condition differs')
    global_deps=[checked[d] for d in u['dependencies'] if unit_by_id(m,d)['condition']=='feature_encoder' and 'held_fold' not in unit_by_id(m,d)]
    inner_deps=[checked[d] for d in u['dependencies'] if unit_by_id(m,d)['id'].startswith('inner')]
    if 'feature_encoder' in done:
        if len(global_deps)!=1 or done['feature_encoder']['checkpoint_sha256']!=global_deps[0]['artifacts']['model.pt']:raise ValueError('loaded global encoder differs from dependency')
    if 'feature_encoder_oof' in done:
        expected=[r0['artifacts']['model.pt'] for r0 in inner_deps]
        if 'held_fold' in u:
            expected=[r0['artifacts']['model.pt'] for r0 in inner_deps if r0['unit']['held_fold']==u['held_fold']]
            if len(expected)!=1:raise ValueError('paired encoder dependency missing')
            expected=expected[0]
        if done['feature_encoder_oof']['checkpoint_sha256']!=expected:raise ValueError('loaded OOF encoder differs from dependency')
    telemetry=Path(root)/safe_rel(r['attempt'])/'telemetry.json'
    if digest(telemetry)!=r['telemetry_sha256']:raise ValueError('telemetry changed')
    checked[uid]=r
    return r


def verify_group(m,gid,root):
    groups=[g for g in m['groups'] if g['id']==gid]
    if len(groups)!=1:raise ValueError('unknown selection group')
    checked={}
    return [verify_unit(m,uid,root,checked) for uid in groups[0]['units']]


@contextlib.contextmanager
def writer_lock(root,uid):
    p=Path(root)/'locks'/f'{uid}.lock';p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a') as f:
        try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise ValueError(f'unit already has writer: {uid}')
        try:yield
        finally:fcntl.flock(f,fcntl.LOCK_UN)


def check_runtime_paths(m):
    configured=os.environ.get('EMOBRAIN_PATHS')
    if not configured or str(Path(configured).resolve())!=m['paths_config']:raise ValueError('runtime EMOBRAIN_PATHS differs from frozen path')
    for key in ('S5_ROI_VOXELS','S5_PM','S4_FEATURES','S4_LABELS'):
        if os.environ.get(key):raise ValueError(f'unreviewed runtime override: {key}')


def check_frozen(m):
    check_runtime_paths(m)
    for rel,sha in m['source_hashes'].items():
        if digest(REPO/safe_rel(rel))!=sha:raise ValueError(f'frozen source changed: {rel}')
    for path,sha in m['external_hashes'].items():
        if digest(path)!=sha:raise ValueError(f'frozen external input changed: {path}')


def science():
    sys.path.insert(0,str(REPO/'src'))
    import s6_train as T
    return T,T.S,T.M,T.c


def independent_roi_preflight(admission):
    """Explicit independent identity route; never asserts Perlmutter equality."""
    import importlib.util
    import numpy as np
    import nibabel as nib
    import pandas as pd
    T,S,M,c=science()
    ad=read_json(admission);bundle=Path(admission).parent
    if digest(admission)!='8473df9924eb6910725b74a3c270348aa4fca7848bd8dd802ebf013f7e5a112f':raise ValueError('unreviewed computational admission')
    chain_path=bundle/'source_hash_chain.json';coverage_path=bundle/'roi_final_check.tsv';responses_path=bundle/'response_bytes.json'
    chain=read_json(chain_path);coverage=pd.read_csv(coverage_path,sep='\t');responses={x['tag']:x for x in read_json(responses_path)['subjects']}
    if chain['identity']!=ad['identity'] or ad['perlmutter_hash_equivalence_claimed']:raise ValueError('wrong independent identity')
    guard_path=REPO/'scripts/b300/verify_s2_roi_voxels.py'
    if digest(guard_path)!=ad['production_guard']['sha256']:raise ValueError('guard differs from admitted version')
    spec=importlib.util.spec_from_file_location('roi_guard',guard_path);guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    table=REPO/'manifests/s2/roi_table.tsv'
    if digest(table)!=ad['roi_table_sha256'] or digest(coverage_path)!=ad['coverage_source_sha256']:raise ValueError('ROI metadata mismatch')
    names=pd.read_csv(table,sep='\t').roi.astype(str).tolist()
    paths={str(p.resolve()):digest(p) for p in (Path(admission),chain_path,coverage_path,responses_path,table)}
    tags={f'{c}_sub-{i:02d}' for c,n in [('hk',5),('mc',6)] for i in range(1,n+1)}
    if {x['tag'] for x in ad['subjects']}!=tags or len(ad['subjects'])!=11:raise ValueError('missing/duplicate ROI subjects')
    for row in ad['subjects']:
        tag=row['tag'];cohort,sub=tag.split('_');dataset,version=('Horikawa','v3') if cohort=='hk' else ('MindCaptioning','v2')
        base=S.P.DATA_ROOT/dataset/sub/f'{version}_qc'
        maskpath=base/f'{sub}_mask_qc.nii.gz';response=base/f'{sub}_blocks_common36_qc_runz.npy';roi=S.P.OUT/'s2_manifest/roi_voxels'/f'{tag}.npz'
        if digest(roi)!=row['sha256'] or digest(maskpath)!=row['mask_sha256']:raise ValueError(f'actual ROI/mask differs: {tag}')
        source=row['source'].split(':',1)[1]
        if chain['historical_remote_hashes'].get(source)!=row['sha256']:raise ValueError('ROI source chain missing')
        if digest(response)!=responses[tag]['sha256']:raise ValueError('response source bytes differ')
        img=nib.load(maskpath);mask=np.asarray(img.dataobj)>0;raw=np.load(response,mmap_mode='r',allow_pickle=False)
        with np.load(roi,allow_pickle=False) as z:
            offsets,cols,ncol=guard.validated_geometry(z,370)
            if z['roi'].tolist()!=names or str(z['mask_sha256'])!=row['mask_sha256']:raise ValueError('ROI order/mask binding differs')
            if not np.array_equal(z['shape'],mask.shape) or not np.array_equal(z['affine'],img.affine):raise ValueError('ROI actual mask geometry differs')
            if ncol!=raw.shape[1] or ncol!=int(mask.sum()):raise ValueError('response/mask column mismatch')
            expected=coverage[(coverage.cohort==cohort)&(coverage.participant==sub)].set_index('roi').loc[names].n_in_qc_mask.to_numpy()
            if not np.array_equal(np.diff(offsets),expected) or np.any(expected<=0):raise ValueError('ROI QC counts differ')
        for p in (roi,maskpath,response):paths[str(p.resolve())]=digest(p)
    return paths


def make_probe(config, freeze, admission, output):
    """Freeze actual source and input bytes without initializing CUDA."""
    T,S,M,c=science()
    from dataclasses import asdict
    c.guard(freeze)
    cfg=S.load_config(config);split=c.load_split();plan=S.load_plan('pilot_fold1',split)
    base=next(x for x in S.candidates('brain_only',k_candidates=cfg.k_candidates,learning_rates=cfg.learning_rates) if x['d']==64 and x['input_wd']==100 and x['lr']==1e-3)
    choices={'brain_only':base}
    for condition in ('feature_encoder','brain_features_only','brain_features_only_paired','brain_frozen_feature_encoder'):
        candidates=S.candidates(condition,base=base,k_candidates=cfg.k_candidates,learning_rates=cfg.learning_rates)
        choices[condition]=next(x for x in candidates if x['lr']==1e-4 and (x['rank'] in (None,8)))
    units=[];groups=[]
    def add(uid,condition,deps,held=None):
        cand=choices[condition];rel=f'{condition}/{S.candidate_id(cand)}_seed0'
        req=['model.pt','done.json','history.tsv']
        if held is not None and condition=='feature_encoder':rel=f'feature_encoder_oof/seed0/inner{held}';req+=['held.npz']
        elif held is not None:rel+=f'/pair{held}';req+=['val_pred.npz']
        elif condition!='feature_encoder':req+=['val_pred.npz']
        u=dict(id=uid,condition=condition,candidate=cand,seed=0,dependencies=deps,artifact_rel=rel,required=req)
        if held is not None:u['held_fold']=held
        units.append(u)
    add('a1','brain_only',[]);add('global','feature_encoder',['a1'])
    held=[int(j) for j,*_ in S.inner_plans(plan,split)]
    for j in held:add(f'inner{j}','feature_encoder',['global'],j)
    prereq=['global']+[f'inner{j}' for j in held]
    add('d3','brain_features_only',prereq)
    for cond,prefix in [('brain_features_only_paired','d3pair'),('brain_frozen_feature_encoder','d4pair')]:
        for j in held:add(f'{prefix}{j}',cond,prereq,j)
    for cond in choices:groups.append(dict(id=cond,units=[u['id'] for u in units if u['condition']==cond and not(u['id'].startswith('inner'))]))
    files=sorted(set((REPO/'src').glob('*.py'))|{S.AUDITION_PATH,Path(__file__),REPO/'scripts/b300/measure_fit_units.py',REPO/'scripts/b300/submit_fit_units.py',REPO/'scripts/b300/verify_s2_roi_voxels.py'})
    inputs={**S.input_paths(plan,stimulus=False),**{f's2:{p.name}':p for p in T.d5.S2_TABLES},'config':Path(config),'admission':Path(admission),'paths_config':Path(os.environ['EMOBRAIN_PATHS'])}
    independent_hashes=independent_roi_preflight(admission)
    import numpy as np
    reference_path=Path(admission).parent/'feature_reference.json'
    reference={x['model']:x for x in read_json(reference_path)['features']}
    independent_hashes[str(reference_path.resolve())]=digest(reference_path)
    for model,role,shape in [('vjepa2','visual_target',[2196,5632]),('deberta','caption_target',[2196,4096])]:
        target=Path(inputs[role]);feature_manifest=target.parent/'manifest.json';fm=read_json(feature_manifest)
        expected=fm.get('target_sha256') or fm['file_sha256']['target.npy']
        if digest(target)!=expected or expected!=reference[model]['sha256'] or list(np.load(target,mmap_mode='r').shape)!=shape:raise ValueError('feature provenance or full shape differs')
        independent_hashes[str(feature_manifest.resolve())]=digest(feature_manifest)
    ad=read_json(admission)
    if ad['computational_admission']!='ROI_INPUTS_PASS_FOR_BOUNDED_RESOURCE_MEASUREMENT':raise ValueError('bounded admission absent')
    for subject in ad['subjects']:
        if subject['tag'].startswith('hk_'):
            roi=inputs['roi:sub-'+subject['tag'][-2:]]
            if digest(roi)!=subject['sha256']:raise ValueError('ROI admission does not bind actual input')
    m=dict(schema=SCHEMA,scope='bounded_measurement',restart_policy='restart_from_seed',plan=plan.name,paths_config=str(Path(os.environ['EMOBRAIN_PATHS']).resolve()),input_roles={k:str(Path(p).resolve()) for k,p in inputs.items()},design_freeze=freeze,config=str(Path(config).resolve()),admission=str(Path(admission).resolve()),units=units,groups=groups,expected_units=[u['id'] for u in units],held_folds=held,candidate_universe={k:[v] for k,v in choices.items()},paired_conditions=['brain_features_only_paired','brain_frozen_feature_encoder'],environment=runtime_environment(),source_commit=c.START_HEAD,source_hashes={str(p.relative_to(REPO)):digest(p) for p in files},external_hashes={**independent_hashes,**{str(Path(p).resolve()):digest(p) for p in inputs.values()}},spec=asdict(S.Spec(seeds=cfg.seeds,input_lr_scale=cfg.input_lr_scale)),numeric_comparison=dict(tensors_rtol=0,tensors_atol=0,predictions_rtol=0,predictions_atol=0,history_rtol=0,history_atol=0),training_targets=34,interpretation_targets=27)
    validate_manifest(m);publish_json(output,m);return m


def clone_dependencies(m,source_root,target_root,target_ids):
    """Byte-identical frozen dependencies for a separate uninterrupted comparator.

    Imported receipts preserve original attempts/job IDs; they are never counted
    as new fits, never rekeyed, and never imported from historical pilot runs.
    """
    import shutil
    source_root=Path(source_root);target_root=Path(target_root)
    if source_root.resolve()==target_root.resolve():raise ValueError('comparator must have separate output root')
    deps=set()
    def visit(uid):
        for dep in unit_by_id(m,uid)['dependencies']:
            if dep not in deps:deps.add(dep);visit(dep)
    for uid in target_ids:visit(uid)
    if deps&set(target_ids):raise ValueError('target cannot also be imported dependency')
    for uid in deps:verify_unit(m,uid,source_root)
    target_root.mkdir(parents=True,exist_ok=False)
    hashes={}
    for u in m['units']:
        uid=u['id']
        if uid not in deps:continue
        r=read_json(receipt_path(source_root,uid));rel=safe_rel(u['artifact_rel'])
        dest=target_root/'science'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(source_root/'science'/rel,dest)
        rp=receipt_path(target_root,uid);rp.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(receipt_path(source_root,uid),rp)
        attempt=safe_rel(r['attempt']);(target_root/attempt).mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source_root/attempt/'telemetry.json',target_root/attempt/'telemetry.json')
        hashes[uid]=digest(rp)
    for uid in deps:verify_unit(m,uid,target_root)
    publish_json(target_root/'imported_dependencies.json',dict(manifest_sha256=identity(m),source_root=str(source_root.resolve()),receipt_hashes=hashes,new_fit_count=0,targets=target_ids,policy='byte-identical same-run frozen dependency import; original job IDs preserved'))


def runtime_environment():
    import platform
    import torch,numpy,pandas
    return dict(python=platform.python_version(),torch=torch.__version__,numpy=numpy.__version__,pandas=pandas.__version__,cuda_build=torch.version.cuda,cudnn=torch.backends.cudnn.version())


def paired_predictions(paths):
    """Same mean-probability operation as FoldRunner._ensemble, with exact row checks."""
    import numpy as np
    parts=[]
    for path in paths:
        with np.load(path,allow_pickle=False) as z:parts.append({k:z[k].copy() for k in z.files})
    if not parts:raise ValueError('no paired predictions')
    keys=[list(zip(z['participant'].tolist(),z['video_id'].tolist())) for z in parts]
    if any(k!=keys[0] for k in keys):raise ValueError('paired prediction row order differs')
    pp=np.stack([z['p'] for z in parts])
    if not np.isfinite(pp).all() or np.any(pp<0) or np.any(pp>1):raise ValueError('invalid paired probabilities')
    pm=pp.mean(0)
    return dict(participant=parts[0]['participant'],video_id=parts[0]['video_id'],p=pm,logit=np.log(pm)-np.log1p(-pm),p_pairs=pp)


def aggregate(m,gid,root):
    import numpy as np
    records=verify_group(m,gid,root)
    by_candidate={}
    for r in records:
        u=r['unit'];done=read_json(Path(root)/'science'/u['artifact_rel']/'done.json')
        by_candidate.setdefault(identity(u['candidate']),[]).append((u,done))
    rows=[]
    for pairs in by_candidate.values():
        vals=[d['val_score'] for _,d in pairs]
        if any(not isinstance(v,(int,float)) or not __import__('math').isfinite(v) for v in vals):raise ValueError('nonfinite validation score')
        rows.append(dict(candidate=pairs[0][0]['candidate'],mean_pair_score=float(np.mean(vals)),units=[u['id'] for u,_ in pairs]))
    # S.select_best has a scientific tie rule; use its candidate fields unchanged.
    _,S,_,_=science()
    scientific=[dict(r['candidate'],candidate_id=S.candidate_id(r['candidate']),val_score=r['mean_pair_score']) for r in rows]
    best=S.select_best(scientific)
    value=dict(scope=m['scope'],manifest_sha256=identity(m),group=gid,rows=rows,best_candidate_id=best['candidate_id'],receipt_hashes={r['unit']['id']:digest(receipt_path(root,r['unit']['id'])) for r in records})
    if gid in m.get('paired_conditions',[]):
        import numpy as np
        chosen=next(r for r in rows if S.candidate_id(r['candidate'])==best['candidate_id'])
        selected=[unit_by_id(m,uid) for uid in chosen['units']]
        out=Path(root)/'aggregations'/gid
        with writer_lock(root,'aggregate-'+gid):
            if out.exists():raise FileExistsError(out)
            tmp=out.parent/(gid+'.tmp-'+uuid.uuid4().hex);tmp.mkdir(parents=True)
            for name in ('val_pred.npz','test_pred.npz'):
                paths=[Path(root)/'science'/u['artifact_rel']/name for u in selected]
                if not any(p.exists() for p in paths):continue
                if not all(p.exists() for p in paths):raise ValueError('incomplete pair prediction universe')
                pred=paired_predictions(paths);pred['held_folds']=np.array([u['held_fold'] for u in selected])
                np.savez(tmp/name,**pred)
            value['ensemble_artifacts']=hash_tree(tmp)
            tmp.rename(out)
    publish_json(Path(root)/'aggregations'/f'{gid}.json',value)
    return value


def build_runner(m,root):
    check_runtime_paths(m)  # Before importing modules that resolve paths from env.
    T,S,M,c=science()
    from dataclasses import asdict
    import torch
    if runtime_environment()!=m['environment']:raise ValueError('runtime software differs from frozen environment')
    c.guard(m['design_freeze'])
    torch.use_deterministic_algorithms(True)
    cfg=S.load_config(m['config']);split=c.load_split();plan=S.load_plan(m['plan'],split);spec=S.Spec(**m['spec'])
    actual_inputs={**S.input_paths(plan,stimulus=False),**{f's2:{p.name}':p for p in T.d5.S2_TABLES},'config':Path(m['config']),'admission':Path(m['admission']),'paths_config':Path(os.environ['EMOBRAIN_PATHS'])}
    if {k:str(Path(p).resolve()) for k,p in actual_inputs.items()}!=m['input_roles']:raise ValueError('resolved runtime input roles differ')
    run=S.Run(m['design_freeze'],{**S.input_paths(plan,stimulus=False),'config':m['config']},stimulus_run_key=None,plan=plan.name,config=asdict(cfg),spec=asdict(spec),torch=torch.__version__,deterministic=torch.are_deterministic_algorithms_enabled(),nondeterministic_ops=[],fit_manifest=identity(m))
    y,v,cap=T.load_known(split,plan,False)
    brains=S.load_brains(split,list(plan.train)+list(plan.val)+list(plan.test))
    fd=S.prepare_fold(brains,split,y,v,cap,plan,device='cuda',roi_keep=S.roi_keep(cfg))
    runner=T.FoldRunner(fd,split,run,spec,cfg,Path(root)/'science');runner.raw=(brains,y,v,cap)
    if plan.test:raise ValueError('bounded measurement must not include outer test')
    return runner


def ensure_selection(m,runner,condition,root):
    """Bind every selection field and checkpoint to the verified complete group."""
    records=verify_group(m,condition,root)
    if any(r['run_key']!=runner.run.key for r in records):raise ValueError('selection dependency run key differs')
    rows=[runner._row(r['unit']['candidate'],read_json(Path(root)/'science'/r['unit']['artifact_rel']/'done.json')) for r in records]
    _,S,_,_=science();best=S.select_best(rows);cand={k:best[k] for k in records[0]['unit']['candidate']}
    chosen=[r for r in records if r['unit']['candidate']==cand]
    seeds={str(r['unit']['seed']):r['unit']['artifact_rel'] for r in chosen}
    if not chosen or len(seeds)!=len(chosen):raise ValueError('ambiguous selected seed mapping')
    for r in chosen:
        u=r['unit'];path=runner.run_dir(condition,cand,u['seed'])
        if str(path.relative_to(runner.root))!=u['artifact_rel']:raise ValueError('selected path differs from receipt-owned path')
        if digest(path/'model.pt')!=r['artifacts']['model.pt']:raise ValueError('selected checkpoint differs from dependency receipt')
    expected=dict(run_key=runner.run.key,condition=condition,candidate=cand,zero_selected=False,source_condition=None,seeds=seeds,rows=rows)
    path=runner.root/condition/'selected.json'
    if path.exists():
        if runner.selected(condition)!=expected:raise ValueError('existing selection structure differs from verified group')
        return expected
    runner._write_selection(condition,rows,cand,None,seeds)
    if runner.selected(condition)!=expected:raise ValueError('published selection differs from verified group')
    return expected


def execute(m,root,ids,telemetry):
    if not os.environ.get('SLURM_JOB_ID'):raise ValueError('GPU execution requires Slurm allocation')
    validate_manifest(m);check_frozen(m)
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    runner=None
    for uid in ids:
        u=unit_by_id(m,uid)
        with writer_lock(root,uid):
            if receipt_path(root,uid).exists():
                verify_unit(m,uid,root);print('SKIP_COMPLETE',uid,flush=True);continue
            for dep in u['dependencies']:verify_unit(m,dep,root)
            check_frozen(m)
            attempt=root/'attempts'/uid/(time.strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]);attempt.mkdir(parents=True)
            artifact=root/'science'/u['artifact_rel']
            if artifact.exists():
                artifact.rename(attempt/'unreceipted_artifact')
            publish_json(attempt/'started.json',dict(unit=uid,manifest_sha256=identity(m),pid=os.getpid(),slurm_job_id=os.environ['SLURM_JOB_ID'],utc=time.time(),policy='restart_from_seed',first_epoch=1))
            try:
                with telemetry(attempt,uid) as meter:
                    if runner is None:
                        with writer_lock(root,'plan'):
                            meter.observe('load_start',None)
                            runner=build_runner(m,root)
                            meter.observe('load_end',None)
                    if u['condition']!='brain_only':
                        with writer_lock(root,'selection-brain_only'):ensure_selection(m,runner,'brain_only',root)
                    if u['id'].startswith('inner') or u['condition'] not in ('brain_only','feature_encoder'):
                        with writer_lock(root,'selection-feature_encoder'):ensure_selection(m,runner,'feature_encoder',root)
                    runner.fit_observer=meter.observe
                    if uid.startswith('inner'):
                        item=next(x for x in runner_plan(runner) if int(x[0])==u['held_fold'])
                        runner.train_inner(u['seed'],*item)
                    elif 'held_fold' in u:
                        enc=next(x for x in runner.oof(u['seed'])['encoders'] if x['fold']==u['held_fold'])
                        fdj=runner._inner_fold_head(enc)
                        runner.train_pair(u['condition'],u['candidate'],u['seed'],enc,fdj)
                        del fdj
                    else:runner.train_one(u['condition'],u['candidate'],u['seed'])
                runner.run.check();check_frozen(m)
                if u['condition']!='brain_only':ensure_selection(m,runner,'brain_only',root)
                if uid.startswith('inner') or u['condition'] not in ('brain_only','feature_encoder'):ensure_selection(m,runner,'feature_encoder',root)
                hashes=hash_tree(artifact)
                if not set(u['required'])<=set(hashes):raise ValueError('incomplete scientific output')
                done=read_json(artifact/'done.json')
                if done['run_key']!=runner.run.key or done['candidate']!=u['candidate'] or done['seed']!=u['seed']:raise ValueError('wrong scientific output identity')
                receipt=dict(status='complete',manifest_sha256=identity(m),unit=u,run_key=runner.run.key,artifacts=hashes,dependencies={dep:digest(receipt_path(root,dep)) for dep in u['dependencies']},attempt=str(attempt.relative_to(root)),telemetry_sha256=digest(attempt/'telemetry.json'),slurm_job_id=os.environ['SLURM_JOB_ID'])
                verify_receipt(m,uid,root,receipt)
                publish_json(receipt_path(root,uid),receipt)
                print('UNIT_COMPLETE',uid,flush=True)
            except BaseException as exc:
                publish_json(attempt/'interrupted_or_failed.json',dict(error=repr(exc),utc=time.time(),resume_semantics='restart_from_seed'))
                raise


def runner_plan(runner):
    _,S,_,_=science();return S.inner_plans(runner.fd.plan,runner.split)


def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('freeze-probe');p.add_argument('--config',required=True);p.add_argument('--design-freeze',required=True);p.add_argument('--admission',required=True);p.add_argument('--output',required=True)
    for cmd in ('validate','run','verify','aggregate','clone-dependencies'):
        p=sub.add_parser(cmd);p.add_argument('--manifest',required=True);p.add_argument('--root');p.add_argument('--units');p.add_argument('--group');p.add_argument('--source-root')
    a=ap.parse_args()
    if a.cmd=='freeze-probe':make_probe(a.config,a.design_freeze,a.admission,a.output);return
    m=validate_manifest(read_json(a.manifest))
    if a.cmd=='validate':check_frozen(m);print(json.dumps({'valid':True,'units':len(m['units']),'manifest_sha256':identity(m)}));return
    if not a.root:ap.error('--root required')
    if a.cmd in ('clone-dependencies','aggregate','verify'):check_frozen(m)
    if a.cmd=='clone-dependencies':
        if not(a.source_root and a.units):ap.error('--source-root and --units required')
        clone_dependencies(m,a.source_root,a.root,a.units.split(','));return
    if a.cmd=='aggregate':
        if not a.group:ap.error('--group required')
        aggregate(m,a.group,a.root);return
    if a.cmd=='verify':
        if a.group:verify_group(m,a.group,a.root)
        else:
            for u in m['units']:verify_unit(m,u['id'],a.root)
        print('VERIFIED');return
    from measure_fit_units import UnitTelemetry
    ids=a.units.split(',') if a.units else m['expected_units']
    execute(m,a.root,ids,UnitTelemetry)

if __name__=='__main__':main()
