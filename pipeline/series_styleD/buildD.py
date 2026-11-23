"""make cutD config for a video key. usage: buildD.py KEY"""
import sys, json, os
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import d_videos as DV
SHIFT = {"152308": 0.24, "152508": -0.18, "152646": 0.52, "152920": -0.20, "153445": -0.20, "153809": -0.20, "153938": 0.46,
         "154207": -0.20, "155958": 0.0, "160054": 0.0}
SHIFT.update(json.load(open(f"{ROOT}/p4/work/shift_extra.json")) if os.path.exists(f"{ROOT}/p4/work/shift_extra.json") else {})
k = sys.argv[1]; C = DV.V[k]
cfg = {"src": f"{ROOT}/p4/src", "work": f"{ROOT}/p4/work/{k}",
       "ranges": [[f"VID_20261109_{c}", a, b] for c, a, b in C["ranges"]],
       "av_shift": {f"VID_20261109_{c}": SHIFT[c] for c in {r[0] for r in C["ranges"]}}, "thr": -33}
os.makedirs(cfg["work"], exist_ok=True)
json.dump(cfg, open(f"{cfg['work']}/cut.json", "w"), indent=1); print(cfg["av_shift"])
