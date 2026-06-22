from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np


EMBEDDING_MODEL = "opencv-haar-gray64-v1"


def box_to_dict(x: int, y: int, w: int, h: int) -> dict:
    return {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}


def box_area(box: dict) -> int:
    return int(box["width"]) * int(box["height"])


class LocalVisionEngine:
    """Small local vision engine.

    This is intentionally replaceable. It gives the API a real working loop now,
    while leaving room to swap in a stronger face model later.
    """

    embedding_model = EMBEDDING_MODEL

    def __init__(self) -> None:
        cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
        self.detector = cv2.CascadeClassifier(str(cascade_path))
        if self.detector.empty():
            raise RuntimeError(f"Could not load OpenCV face cascade at {cascade_path}")

    def read_image(self, image_path: Path) -> np.ndarray:
        data = np.fromfile(str(image_path), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        return image

    def detect_faces(
        self,
        image: np.ndarray,
        fallback_to_full_image: bool = False,
    ) -> list[dict]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale(
            gray,
            scaleFactor=1.08,
            minNeighbors=5,
            minSize=(36, 36),
        )
        boxes = [box_to_dict(x, y, w, h) for (x, y, w, h) in faces]
        boxes.sort(key=box_area, reverse=True)

        if not boxes and fallback_to_full_image:
            height, width = image.shape[:2]
            boxes = [box_to_dict(0, 0, width, height)]

        return boxes

    def embedding(self, image: np.ndarray, box: dict) -> list[float]:
        crop = self.crop(image, box)
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)
        gray = cv2.equalizeHist(gray)
        vector = gray.astype(np.float32).reshape(-1) / 255.0
        vector = vector - float(vector.mean())
        norm = float(np.linalg.norm(vector))
        if norm > 0:
            vector = vector / norm
        return vector.astype(float).tolist()

    def quality_score(self, image: np.ndarray, box: dict) -> float:
        crop = self.crop(image, box)
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        image_area = max(1, image.shape[0] * image.shape[1])
        relative_area = min(1.0, box_area(box) / image_area * 8.0)
        sharpness_score = min(1.0, math.log1p(sharpness) / 8.0)
        return round((relative_area * 0.45) + (sharpness_score * 0.55), 4)

    def crop(self, image: np.ndarray, box: dict) -> np.ndarray:
        height, width = image.shape[:2]
        x = max(0, int(box["x"]))
        y = max(0, int(box["y"]))
        w = max(1, int(box["width"]))
        h = max(1, int(box["height"]))
        return image[y : min(height, y + h), x : min(width, x + w)]

    def similarity(self, left: list[float], right: list[float]) -> float:
        a = np.asarray(left, dtype=np.float32)
        b = np.asarray(right, dtype=np.float32)
        if a.size == 0 or b.size == 0 or a.size != b.size:
            return 0.0
        score = float(np.dot(a, b))
        return round(max(0.0, min(1.0, (score + 1.0) / 2.0)), 4)

