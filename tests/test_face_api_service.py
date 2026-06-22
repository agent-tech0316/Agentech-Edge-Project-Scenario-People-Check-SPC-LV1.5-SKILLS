from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from sa_attendance_system.service import SAAttendanceService


class FaceAPIServiceTest(unittest.TestCase):
    def test_enroll_and_recognize_with_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image_path = root / "face.jpg"
            image = Image.new("RGB", (160, 160), "white")
            draw = ImageDraw.Draw(image)
            draw.ellipse((45, 30, 115, 100), fill=(210, 170, 130))
            draw.ellipse((62, 55, 70, 63), fill="black")
            draw.ellipse((90, 55, 98, 63), fill="black")
            draw.arc((65, 65, 98, 90), 0, 180, fill="black", width=2)
            image.save(image_path)

            service = SAAttendanceService(
                db_path=root / "attendance.sqlite",
                media_dir=root / "media",
            )
            person = service.create_person("Test Student", person_type="student")
            service.enroll_face(
                person_id=person["id"],
                image_bytes=image_path.read_bytes(),
                filename=image_path.name,
                fallback_to_full_image=True,
            )
            result = service.recognize_image(
                image_bytes=image_path.read_bytes(),
                filename=image_path.name,
                fallback_to_full_image=True,
            )

            self.assertEqual(result["face_count"], 1)
            self.assertEqual(result["faces"][0]["status"], "matched")
            self.assertEqual(
                result["faces"][0]["best_candidate"]["person"]["display_name"],
                "Test Student",
            )


if __name__ == "__main__":
    unittest.main()

