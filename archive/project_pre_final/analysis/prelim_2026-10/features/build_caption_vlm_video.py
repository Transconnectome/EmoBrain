#!/usr/bin/env python3
"""영상 입력 VLM 캡션 (2026-10-29).

v1 (EmoViS captions.json) 은 Qwen2.5-VL-7B 에 정지 프레임 3장(25·50·75% 지점)을 넣어 만들었고, 무작위 24개 중 7개에서
핵심 사건·대상이 틀리거나 성적 행위가 빠졌다 (project/output/prelim_2026-10/11_caption_qc/README.md).
여기서는 영상 전체에서 초당 2장(최소 4장, 최대 32장, 긴 변 448 px 이하)을 시간 순서대로 영상 입력으로 넣는다.
프롬프트와 생성 설정(greedy, 최대 256 토큰)은 v1 과 같다. 사람 캡션은 쓰지 않는다.

generate : 영상 1~2185 (또는 --ids) 캡션. --shard k --nshards n 으로 GPU 마다 나눠 돌린다. 영상마다 parts/shard<k>of<n>.jsonl (--ids 면 pilot.jsonl) 에
           한 줄씩 쓰고, 다시 돌리면 끝난 영상은 건너뛴다 (확인 목록으로 먼저 돌린 영상도 전체 실행에서 그대로 쓴다).
merge    : parts 를 모아 captions.json (키 = 영상 번호) 을 쓰고, 2185개가 다 있으면 all-mpnet-base-v2 임베딩을
           <특징 폴더>/caption_<태그>_mpnet.npy + _video_id.tsv 로 저장한다 (2186~2196 = canonical 1~11 행, build_lab_features 규칙).
출력: <특징 폴더>/caption_vlm_video/<태그>/{parts/, captions.json, build_info.json}
사용: python build_caption_vlm_video.py generate|merge --model <HF 이름> --feat <특징 폴더> --bundle <자극 묶음> --videos <mp4 폴더>
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import build_lab_features as blf  # noqa: E402

N = 2185
PROMPT = "Describe the setting, objects, people, actions, and events visible in this video. Do not name any emotions."
FPS, MIN_F, MAX_F, MAX_SIDE, DECODE_FPS = 2.0, 4, 32, 448, 8.0
MAX_NEW_TOKENS = 256
FFMPEG = "/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffmpeg"  # 시스템 ffmpeg 에는 h264 디코더가 없다
FFPROBE = "/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffprobe"
TAGS = {"Qwen/Qwen2.5-VL-7B-Instruct": "qwen25vl7b_video", "Qwen/Qwen3-VL-8B-Instruct": "qwen3vl8b_video",
        "Qwen/Qwen3-VL-2B-Instruct": "qwen3vl2b_video"}


def tag_of(model):
    return TAGS.get(model, model.split("/")[-1].lower().replace("-", "").replace(".", "") + "_video")


def read_frames(path):
    """초당 DECODE_FPS 장으로 풀고, 그중 초당 FPS 장 (MIN_F~MAX_F, 짝수) 을 시간 간격이 고르게 고른다."""
    pr = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                         "-of", "json", str(path)], capture_output=True, text=True, check=True)
    info = json.loads(pr.stdout); w, h = info["streams"][0]["width"], info["streams"][0]["height"]
    dur = float(info["format"]["duration"])
    s = min(1.0, MAX_SIDE / max(w, h)); W, H = max(28, int(w * s) // 2 * 2), max(28, int(h * s) // 2 * 2)
    raw = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-vf", f"fps={DECODE_FPS},scale={W}:{H}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    arr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    n = int(np.clip(round(dur * FPS), MIN_F, MAX_F)); n += n % 2
    idx = np.linspace(0, len(arr) - 1, n).round().astype(int)
    return arr[idx], idx, len(arr), dur


class Captioner:
    def __init__(self, model, device):
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor
        self.torch, self.device, self.qwen3 = torch, device, "Qwen3-VL" in model
        self.proc = AutoProcessor.from_pretrained(model)
        self.model = AutoModelForImageTextToText.from_pretrained(model, dtype=torch.bfloat16, attn_implementation="sdpa").to(device).eval()

    def __call__(self, frames, idx, n_decoded, dur, max_new_tokens=MAX_NEW_TOKENS):
        msgs = [{"role": "user", "content": [{"type": "video"}, {"type": "text", "text": PROMPT}]}]
        text = self.proc.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        if self.qwen3:
            from transformers.video_utils import VideoMetadata
            meta = VideoMetadata(total_num_frames=n_decoded, fps=DECODE_FPS, frames_indices=idx.tolist(), duration=dur)
            kw = dict(video_metadata=[meta], do_sample_frames=False)
        else:
            kw = dict(fps=float(np.clip((len(idx) - 1) / max(dur, 1e-3), 0.5, 24.0)), do_sample_frames=False)
        inp = self.proc(text=[text], videos=[frames], return_tensors="pt", **kw).to(self.device)
        with self.torch.no_grad():
            out = self.model.generate(**inp, max_new_tokens=max_new_tokens, do_sample=False)
        return self.proc.batch_decode(out[:, inp["input_ids"].shape[1]:], skip_special_tokens=True)[0].strip(), int(inp["input_ids"].shape[1])


def done_ids(parts):
    ids = set()
    for p in parts.glob("*.jsonl"):
        for line in p.read_text().splitlines():
            r = json.loads(line)
            if "caption" in r:
                ids.add(r["video_id"])
    return ids


def generate(a):
    root = a.feat / "caption_vlm_video" / tag_of(a.model); parts = root / "parts"; parts.mkdir(parents=True, exist_ok=True)
    ids = [int(x) for x in a.ids.split(",")] if a.ids else list(range(1, N + 1))
    ids = [v for i, v in enumerate(ids) if i % a.nshards == a.shard]
    todo = [v for v in ids if v not in done_ids(parts)]
    print(f"{a.model} shard {a.shard}/{a.nshards}: 대상 {len(ids)}, 남은 것 {len(todo)}", flush=True)
    if not todo:
        return
    cap = Captioner(a.model, a.device); out = parts / ("pilot.jsonl" if a.ids else f"shard{a.shard}of{a.nshards}.jsonl")
    for k, v in enumerate(todo):
        t0 = time.time()
        try:
            frames, idx, nd, dur = read_frames(a.videos / f"{v:04d}.mp4")
            text, ntok = cap(frames, idx, nd, dur, a.max_new_tokens)
            rec = dict(video_id=v, caption=text, n_frames=len(idx), duration=round(dur, 3), frame_hw=list(frames.shape[1:3]),
                       n_input_tokens=ntok, seconds=round(time.time() - t0, 1))
        except Exception as e:  # 영상 하나가 실패해도 계속하고 기록만 남긴다
            rec = dict(video_id=v, error=f"{type(e).__name__}: {e}")
        with open(out, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if k % 20 == 0 or "error" in rec:
            print(f"[{k + 1}/{len(todo)}] video {v} {rec.get('seconds', '')}s {rec.get('error', rec.get('caption', '')[:80])}", flush=True)


def merge(a):
    tag = tag_of(a.model); root = a.feat / "caption_vlm_video" / tag
    recs = {}
    for p in sorted((root / "parts").glob("*.jsonl")):
        for line in p.read_text().splitlines():
            r = json.loads(line)
            if "caption" in r:
                recs[r["video_id"]] = r
    caps = {str(v): recs[v]["caption"] for v in sorted(recs)}
    (root / "captions.json").write_text(json.dumps(caps, ensure_ascii=False, indent=0))
    missing = [v for v in range(1, N + 1) if v not in recs]
    info = dict(model=a.model, prompt=PROMPT, frames=f"{FPS}/s, {MIN_F}~{MAX_F}, long side <= {MAX_SIDE}", greedy=True,
                max_new_tokens=MAX_NEW_TOKENS, n_captions=len(caps), n_missing=len(missing),
                mean_seconds=float(np.mean([r["seconds"] for r in recs.values()])) if recs else None)
    print(json.dumps(info, ensure_ascii=False, indent=1))
    if missing:
        print(f"아직 {len(missing)}개 없음 (예: {missing[:10]}). 임베딩은 2185개가 다 모인 뒤 만든다.")
    else:
        X = blf.expand_2185(blf.Encoder(a.device)([caps[str(v)] for v in range(1, N + 1)]), blf.read_crosswalk(a.bundle))
        name = f"caption_{tag}_mpnet"
        np.save(a.feat / f"{name}.npy", X.astype(np.float32))
        pd.DataFrame(dict(video_id=np.arange(1, blf.N_VIDEOS + 1))).to_csv(a.feat / f"{name}_video_id.tsv", sep="\t", index=False)
        info["feature"] = name
    (root / "build_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["generate", "merge"]); ap.add_argument("--model", default="Qwen/Qwen2.5-VL-7B-Instruct")
    ap.add_argument("--feat", type=Path, required=True); ap.add_argument("--bundle", type=Path); ap.add_argument("--videos", type=Path)
    ap.add_argument("--ids"); ap.add_argument("--shard", type=int, default=0); ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--device", default="cuda"); ap.add_argument("--max-new-tokens", type=int, default=MAX_NEW_TOKENS)
    a = ap.parse_args()
    generate(a) if a.cmd == "generate" else merge(a)


if __name__ == "__main__":
    main()
