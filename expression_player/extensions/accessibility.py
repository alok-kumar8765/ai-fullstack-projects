from utils.logger import setup_logger

logger = setup_logger("AccessibilityExtension")

class AccessibilityExtension:
    """Assistive communication and accessibility configuration module."""
    def __init__(self, high_contrast: bool = False, large_fonts: bool = False):
        self.high_contrast = high_contrast
        self.large_fonts = large_fonts
        logger.info("Accessibility extension initialized.")

    def get_font_configuration(self) -> dict:
        if self.large_fonts:
            return {"family": "Segoe UI", "size": 16, "weight": "bold"}
        return {"family": "Segoe UI", "size": 10, "weight": "normal"}

    def toggle_high_contrast(self) -> bool:
        self.high_contrast = not self.high_contrast
        return self.high_contrast