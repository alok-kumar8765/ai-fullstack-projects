import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from utils.preprocessing import preprocess_signature

def configure_gpu_settings():
    """Configures TensorFlow hardware acceleration and dynamic VRAM growth."""
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"🚀 [AI Engine] TensorFlow is utilizing {len(gpus)} GPU(s) with dynamic memory allocation.")
        except RuntimeError as e:
            print(f"⚠️ GPU configuration error: {e}")
    else:
        print("💻 [AI Engine] No physical GPU detected. Falling back to CPU execution mode.")

def load_siamese_model(model_path):
    configure_gpu_settings()
    try:
        model = load_model(model_path, compile=False)
        print("✅ Pre-trained Siamese model weights loaded successfully.")
        return model
    except Exception:
        print("⚠️ Warning: Pre-trained weights not found. Initializing skeleton baseline model.")
        return build_base_siamese_network()

def build_base_siamese_network():
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
    Compares a single reference signature against a test signature 
    using embedding generation and cosine similarity calculation.
    """
    ref_img = preprocess_signature(ref_path)
    test_img = preprocess_signature(test_path)
    
    # Insert batch dimension
    ref_img = np.expand_dims(ref_img, axis=0)
    test_img = np.expand_dims(test_img, axis=0)
    
    # Extract feature embeddings
    emb1 = model.predict(ref_img, verbose=0)
    emb2 = model.predict(test_img, verbose=0)
    
    # Cosine Similarity Formula Calculation
    dot_product = np.dot(emb1[0], emb2[0])
    norm_a = np.linalg.norm(emb1[0])
    norm_b = np.linalg.norm(emb2[0])
    
    if norm_a == 0 or norm_b == 0:
        similarity = 0.0
    else:
        similarity = dot_product / (norm_a * norm_b)
        
    # Scale from [-1, 1] cosine range to percentage boundary [0, 1]
    similarity_score = float((similarity + 1) / 2)
    is_genuine = similarity_score >= threshold
    
    return is_genuine, similarity_score