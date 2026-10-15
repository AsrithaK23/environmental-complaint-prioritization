
import sys
import unittest
from pathlib import Path

# Make the project root importable when running this file directly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.predict import predict_complaint


class TestComplaintPredictions(unittest.TestCase):

    def test_waste_management(self):
        result = predict_complaint(
            "Garbage has not been collected near the hostel."
        )
        self.assertEqual(result["category"], "Waste Management")

    def test_water_sanitation(self):
        result = predict_complaint(
            "There is no drinking water in the college building."
        )
        self.assertEqual(result["category"], "Water / Sanitation")

    def test_air_pollution(self):
        result = predict_complaint(
            "Smoke from burning plastic is affecting students."
        )
        self.assertEqual(result["category"], "Air Pollution")

    def test_noise_pollution(self):
        result = predict_complaint(
            "Loud construction noise disturbs students in class."
        )
        self.assertEqual(result["category"], "Noise Pollution")

    def test_energy_issue(self):
        result = predict_complaint(
            "Streetlights are not working along the campus pathway."
        )
        self.assertEqual(result["category"], "Energy-related Issues")

    def test_greenery(self):
        result = predict_complaint(
            "Plants in the college garden are dying."
        )
        self.assertEqual(result["category"], "Greenery / Landscaping")

    
    def test_other(self):
        result = predict_complaint(
            "An administrative issue unrelated to waste, water, "
            "air, noise, energy, or campus greenery needs attention."
        )
        self.assertIn(
            result["category"],
            {
                "Waste Management",
                "Water / Sanitation",
                "Air Pollution",
                "Noise Pollution",
                "Energy-related Issues",
                "Greenery / Landscaping",
                "Other",
            },
        )


    def test_confidence_is_valid(self):
        result = predict_complaint(
            "Overflowing garbage bins smell bad near the hostel."
        )
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)

    def test_review_flag_exists(self):
        result = predict_complaint(
            "There is an environmental problem."
        )
        self.assertIn("needs_review", result)
        self.assertIsInstance(result["needs_review"], bool)

    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            predict_complaint("")

    def test_non_text_only_input_rejected(self):
        with self.assertRaises(ValueError):
            predict_complaint("!!! 123 ###")


if __name__ == "__main__":
    unittest.main(verbosity=2)
