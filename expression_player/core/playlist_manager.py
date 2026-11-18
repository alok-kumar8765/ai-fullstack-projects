import random
from pathlib import Path
from typing import List, Optional
from utils.logger import setup_logger

logger = setup_logger("PlaylistManager")

class PlaylistManager:
    def __init__(self, music_dir: str = "music"):
        self.music_dir = Path(music_dir)
        self.categories = ["happy", "sad", "angry", "surprise", "neutral"]
        self.ensure_directories()

    def ensure_directories(self) -> None:
        self.music_dir.mkdir(exist_ok=True, parents=True)
        for cat in self.categories:
            (self.music_dir / cat).mkdir(exist_ok=True)

    def get_tracks(self, emotion: str) -> List[Path]:
        cat_dir = self.music_dir / emotion.lower()
        if not cat_dir.exists():
            cat_dir = self.music_dir / "neutral"
        
        tracks = list(cat_dir.glob("*.mp3")) + list(cat_dir.glob("*.wav"))
        if not tracks:
            # Fallback to general music dir if category is empty
            tracks = list(self.music_dir.glob("**/*.mp3"))
        return tracks

    def get_random_track(self, emotion: str) -> Optional[Path]:
        tracks = self.get_tracks(emotion)
        if not tracks:
            logger.warning("No audio tracks found in directory: %s", self.music_dir)
            return None
        return random.choice(tracks)