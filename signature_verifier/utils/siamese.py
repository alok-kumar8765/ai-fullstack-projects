import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from utils.preprocessing import preprocess_signature

def load_siamese_model(model_path):
    # If a pre-trained model file exists, load it. Otherwise, construct a baseline architecture.
    try:
        model = load_model(model_path, compile=False)
        return model
    except Exception:
        # Fallback dummy/base model structure builder if file doesn't exist yet
        print("Warning: Pre-trained weights not found. Initializing architecture skeleton.")
        return build_base_siamese_network()

def build_base_siamese_network():
    # Embedding feature extractor network skeleton
    input_sig = tf.keras.Input(shape=(155, 220, 1))
    x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu')(input_sig)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu')(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.layers.Dense(128, activation='relu')(x)
    return Model(input_sig, x)

def verify_signatures(model, ref_path, test_path, threshold=0.75):
    """
    Compares reference signature and test signature embeddings.
    Returns boolean (is_genuine) and similarity score.
    """
    ref_img = preprocess_signature(ref_path)
    test_img = preprocess_signature(test_path)
    
    # Add batch dimension
    ref_img = np.expand_dims(ref_img, axis=0)
    test_img = np.expand_dims(test_img, axis=0)
    
    # Get feature embeddings
    emb1 = model.predict(ref_img)
    emb2 = model.predict(test_img)
    
    # Compute Cosine Similarity or Euclidean Distance
    # Using cosine similarity here (-1 to 1, normalized)
    dot_product = np.dot(emb1[0], emb2[0])
    norm_a = np.linalg.norm(emb1[0])
    norm_b = np.linalg.norm(emb2[0])
    
    if norm_a == 0 or norm_b == 0:
        similarity = 0.0
    else:
        similarity = dot_product / (norm_a * norm_b)
        
    # Map cosine similarity to 0-1 range roughly if needed, or threshold directly
    similarity_score = float((similarity + 1) / 2) # scale -1..1 to 0..1
    
    is_genuine = similarity_score >= threshold
    return is_genuine, similarity_score