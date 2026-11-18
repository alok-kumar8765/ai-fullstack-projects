import cv2
import numpy as np

def preprocess_signature(image_path, target_size=(220, 155)):
    """
    Reads a signature image, converts to grayscale, applies Otsu thresholding,
    crops tightly to its bounding box, and normalizes it for the Siamese network.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Invert and threshold to isolate crisp binary signature lines
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find bounding box to crop out unnecessary whitespace
    coords = cv2.findNonZero(thresh)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        cropped = thresh[y:y+h, x:x+w]
    else:
        cropped = thresh
        
    # Resize keeping aspect ratio mapping to target network dimensions
    resized = cv2.resize(cropped, target_size, interpolation=cv2.INTER_AREA)
    
    # Scale pixels to range [0.0, 1.0]
    normalized = resized.astype("float32") / 255.0
    
    # Expand dimensions to structural shape (Height, Width, Channels)
    return np.expand_dims(normalized, axis=-1)