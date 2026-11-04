"""Build a 3D LUT (.cube) that converts iPhone HLG / BT.2020 video to SDR BT.709 for platforms that can't show HDR.

HLG inverse OETF -> HLG OOTF (1000-nit display, gamma 1.2) -> BT.2020-to-BT.709 primaries -> normalise to the
203-nit reference white -> soft highlight shoulder (linear up to KNEE, then an exponential roll-off towards 1.0, so
skin and bright walls keep detail instead of clipping glossy-white) -> BT.709 display gamma 1/2.4.
Usage: python3 -I tools/hlg_to_sdr_lut.py out.cube [--knee 0.6] [--gain 1.0]
"""

import sys

import numpy as np

N = 65
KNEE = float(sys.argv[sys.argv.index("--knee") + 1]) if "--knee" in sys.argv else 0.6
GAIN = float(sys.argv[sys.argv.index("--gain") + 1]) if "--gain" in sys.argv else 1.0
A, B, C = 0.17883277, 0.28466892, 0.55991073


def hlg_inv_oetf(e):
    return np.where(e <= 0.5, e * e / 3.0, (np.exp((e - C) / A) + B) / 12.0)


M2020_709 = np.array([[1.6605, -0.5876, -0.0728], [-0.1246, 1.1329, -0.0083], [-0.0182, -0.1006, 1.1187]])

g = np.linspace(0, 1, N)
b, gg, r = np.meshgrid(g, g, g, indexing="ij")  # .cube order: red changes fastest
rgb = np.stack([r, gg, b], -1).reshape(-1, 3)
scene = hlg_inv_oetf(rgb)
ys = scene @ np.array([0.2627, 0.6780, 0.0593])
disp = 1000.0 * (np.maximum(ys, 1e-6) ** 0.2)[:, None] * scene  # OOTF, nits (BT.2020)
lin = np.clip(disp @ M2020_709.T, 0, None) / 203.0 * GAIN
shoulder = KNEE + (1 - KNEE) * (1 - np.exp(-(lin - KNEE) / (1 - KNEE)))
out = np.where(lin <= KNEE, lin, shoulder)
out = np.clip(out, 0, 1) ** (1 / 2.4)
with open(sys.argv[1], "w") as f:
    f.write(f"LUT_3D_SIZE {N}\n")
    for v in out:
        f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
print(sys.argv[1], f"knee {KNEE} gain {GAIN}")
