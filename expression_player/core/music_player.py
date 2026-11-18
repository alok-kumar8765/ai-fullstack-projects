import pygame
from pathlib import Path
from typing import Optional
from core.playlist_manager import PlaylistManager
from utils.logger import setup_logger

logger = setup_logger("MusicPlayer")

class MusicPlayer:
    def __init__(self, music_dir: str = "music", volume: float = 0.7):
        self.playlist_manager = PlaylistManager(music_dir)
        self.current_track: Optional[Path] = None
        self.current_category: Optional[str] = None
        self.is_playing = False
        self.is_paused = False
        self.volume = volume

        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(self.volume)
            logger.info("Pygame mixer initialized successfully.")
        except Exception as e:
            logger.error("Failed to initialize Pygame mixer: %s", e)

    def play_for_emotion(self, emotion: str, force: bool = False) -> Optional[str]:
        if not force and self.current_category == emotion and self.is_playing:
            return self.current_track.name if self.current_track else None

        track = self.playlist_manager.get_random_track(emotion)
        if not track:
            logger.warning("No track available for emotion: %s", emotion)
            return None

        try:
            pygame.mixer.music.load(str(track))
            pygame.mixer.music.play()
            self.current_track = track
            self.current_category = emotion
            self.is_playing = True
            self.is_paused = False
            logger.info("Playing track %s for confirmed emotion %s", track.name, emotion)
            return track.name
        except Exception as e:
            logger.error("Error playing audio track %s: %s", track, e)
            return None

    def toggle_play_pause(self) -> bool:
        if not self.is_playing and not self.is_paused:
            track = self.playlist_manager.get_random_track("neutral")
            if track:
                pygame.mixer.music.load(str(track))
                pygame.mixer.music.play()
                self.current_track = track
                self.is_playing = True
                self.is_paused = False
            return self.is_playing

        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.is_playing = True
        elif self.is_playing:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.is_playing = False
        return self.is_playing

    def stop(self) -> None:
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        logger.info("Music playback stopped.")

    def set_volume(self, volume: float) -> None:
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)

    def next_track(self) -> Optional[str]:
        if self.current_category:
            return self.play_for_emotion(self.current_category, force=True)
        return None