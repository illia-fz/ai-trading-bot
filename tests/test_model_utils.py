import os
import unittest
from unittest import mock
from model_utils import analyze_text_with_model


class TestModelUtils(unittest.TestCase):
    def test_default_behavior_without_api_keys(self):
        # When no API endpoints or keys are configured, the model should return hold
        with mock.patch.dict(os.environ, {}, clear=True):
            result = analyze_text_with_model("This is a test.")
            self.assertEqual(result["label"], "hold")
            self.assertEqual(result["score"], 0.0)

    def test_openai_mode_without_keys(self):
        # Setting a model API url without keys should still return default hold
        with mock.patch.dict(os.environ, {"MODEL_API_URL": "https://api.openai.com/v1"}, clear=True):
            result = analyze_text_with_model("Another test.")
            self.assertEqual(result["label"], "hold")
            self.assertEqual(result["score"], 0.0)


if __name__ == "__main__":
    unittest.main()
