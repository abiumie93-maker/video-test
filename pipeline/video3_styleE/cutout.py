import numpy as np, cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
class Cutter:
    def __init__(self, model):
        self.seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
            base_options=BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.VIDEO, output_confidence_masks=True))
        self.k = 0; self.prev = None
    def mask(self, rgb):
        small = cv2.resize(rgb, (rgb.shape[1] // 2, rgb.shape[0] // 2), interpolation=cv2.INTER_AREA)
        r = self.seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(small)), self.k * 33); self.k += 1
        m = r.confidence_masks[0].numpy_view().copy()
        m = cv2.resize(m, (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_LINEAR)
        m = np.clip((m - 0.35) / 0.3, 0, 1)
        if self.prev is not None: m = 0.6 * m + 0.4 * self.prev     # temporal smoothing (less edge flicker)
        self.prev = m
        return m
def stylise(rgb, keep_product=True):
    """B&W with mild contrast; keep strongly saturated orange/green packaging in colour."""
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    g = np.clip((g - 128) * 1.18 + 128 + 6, 0, 255)
    bw = np.repeat(g[..., None], 3, 2)
    if not keep_product: return bw.astype(np.uint8)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255
    orange = ((h >= 8) & (h <= 45)) & (s > 0.62) & (v > 0.35)
    k = cv2.GaussianBlur(orange.astype(np.float32), (0, 0), 3)
    k = np.clip(k * 1.6, 0, 1)[..., None]
    return (bw * (1 - k) + rgb.astype(np.float32) * k).astype(np.uint8)
def sticker(rgb_styled, m, outline=14):
    """returns RGBA with white sticker outline + soft shadow (same size)"""
    a = (m * 255).astype(np.uint8)
    hard = (m > 0.5).astype(np.uint8) * 255
    dil = cv2.dilate(hard, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (outline * 2 + 1, outline * 2 + 1)))
    dil = cv2.GaussianBlur(dil, (0, 0), 1.2)
    out = np.zeros((*m.shape, 4), np.uint8)
    out[..., :3] = 255; out[..., 3] = dil
    af = (a.astype(np.float32) / 255)[..., None]
    out[..., :3] = (rgb_styled * af + 255 * (1 - af)).astype(np.uint8)
    return out

def grade(rgb, warm=0.04, sat=1.12, contrast=1.10, lift=6):
    """clean, warm, punchy colour grade for indoor phone footage"""
    x = rgb.astype(np.float32) / 255.0
    # gentle S-curve contrast around mid-grey + slight lift
    x = np.clip((x - 0.5) * contrast + 0.5, 0, 1)
    x = x + (lift / 255.0) * (1 - x)
    # saturation (luma-preserving)
    l = (0.299 * x[..., 0] + 0.587 * x[..., 1] + 0.114 * x[..., 2])[..., None]
    x = np.clip(l + (x - l) * sat, 0, 1)
    # warm highlights / slightly cool shadows (teal-orange, subtle)
    hi = np.clip((l - 0.45) / 0.55, 0, 1); sh = np.clip((0.45 - l) / 0.45, 0, 1)
    x[..., 0] += warm * hi[..., 0]; x[..., 2] -= warm * 0.8 * hi[..., 0]
    x[..., 2] += 0.02 * sh[..., 0]; x[..., 0] -= 0.01 * sh[..., 0]
    # soft skin protect: avoid over-red skin
    return (np.clip(x, 0, 1) * 255).astype(np.uint8)
