import cv2
import numpy as np

def preprocess_signature(image_path, target_size=(220, 155)):
    """
    Reads a signature image, converts to grayscale, applies thresholding,
    crops to bounding box or pads, and resizes to target network dimensions.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Invert and threshold to get crisp binary signature lines
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find bounding box of the signature to center it
    coords = cv2.findNonZero(thresh)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        cropped = thresh[y:y+h, x:x+w]
    else:
        cropped = thresh
        
    # Resize keeping aspect ratio or direct resize to target size
    resized = cv2.resize(cropped, target_size, interpolation=cv2.INTER_AREA)
    
    # Normalize pixel values between 0 and 1
    normalized = resized.astype("float32") / 255.0
    
    # Expand dims for model input shape (Batch, Height, Width, Channels)
    return np.expand_dims(normalized, axis=-1)