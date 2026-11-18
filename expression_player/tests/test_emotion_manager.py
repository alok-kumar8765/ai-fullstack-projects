import unittest
from core.emotion_manager import EmotionManager

class TestEmotionManager(unittest.TestCase):
    def setUp(self):
        self.manager = EmotionManager(confidence_threshold=0.6, debounce_duration=0.0, window_size=3)

    def test_confidence_filtering(self):
        low_conf_detection = {"emotion": "happy", "confidence": 0.4}
        result = self.manager.process_detection(low_conf_detection)
        self.assertIsNone(result)

    def test_emotion_transition(self):
        # Fill rolling window with 'happy'
        self.manager.process_detection({"emotion": "happy", "confidence": 0.9})
        self.manager.process_detection({"emotion": "happy", "confidence": 0.9})
        confirmed = self.manager.process_detection({"emotion": "happy", "confidence": 0.9})
        
        self.assertEqual(confirmed, "happy")
        self.assertEqual(self.manager.current_emotion, "happy")

if __name__ == "__main__":
    unittest.main()