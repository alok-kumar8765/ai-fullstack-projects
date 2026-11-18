import random
import numpy as np
import tensorflow as tf
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


# Build CNN Architecture
def build_ai_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(128, 128, 3)),
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(3, activation='softmax'),  # [Left, Straight, Right]
    ])
    model.compile(
        optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy']
    )
    return model


ai_model = build_ai_model()


def generate_track_data(seed):
    random.seed(seed)
    np.random.seed(seed)
    num_points = 12
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    waypoints = []

    for angle in angles:
        radius = random.uniform(40, 80)
        x = round(np.cos(angle) * radius, 2)
        z = round(np.sin(angle) * radius, 2)
        waypoints.append({'x': x, 'z': z})

    track_length = round(random.uniform(3.5, 6.2), 1)
    difficulty = random.choice(['Easy', 'Medium', 'Hard'])

    return {
        'seed': seed,
        'waypoints': waypoints,
        'length': f'{track_length} km',
        'difficulty': difficulty,
        'status': 'AI Racing Track Generated Successfully!',
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate_track', methods=['POST'])
def api_generate_track():
    seed = request.json.get('seed', random.randint(1, 1000))
    return jsonify(generate_track_data(seed))


@app.route('/predict_move', methods=['POST'])
def predict_move():
    # Simulate a camera frame input into the TensorFlow model
    dummy_frame = np.random.rand(1, 128, 128, 3).astype(np.float32)
    prediction = ai_model.predict(dummy_frame, verbose=0)
    action = int(np.argmax(prediction))  # 0: Left, 1: Straight, 2: Right
    return jsonify({'action': action})


if __name__ == '__main__':
    print('Starting AI Racing Server at http://localhost:5000')
    app.run(debug=True, port=5000)