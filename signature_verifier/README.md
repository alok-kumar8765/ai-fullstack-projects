# AI-Powered Signature Verifier

> An advanced, secure, and lightweight web application built with **Flask**, **TensorFlow/Keras**, and **OpenCV** to authenticate and verify handwritten signatures using Siamese Neural Networks.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?style=for-the-badge&logo=flask&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?style=for-the-badge&logo=tensorflow&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
[![GitHub Owner](https://img.shields.io/badge/GitHub-alok--kumar8765-lightgrey?style=for-the-badge&logo=github)](https://github.com/alok-kumar8765)

---

## 📋 Table of Contents
1. [Purpose of This Project](#-purpose-of-this-project)
2. [Folder Structure](#-folder-structure)
3. [Architecture Diagram](#-architecture-diagram)
4. [Data Flow Diagram (DFD)](#-data-flow-diagram-dfd)
5. [Entity-Relationship (ER) Diagram](#-entity-relationship-er-diagram)
6. [Installation & Setup Guide](#-installation--setup-guide)
7. [How to Use](#-how-to-use)
8. [Pros & Cons](#-pros--cons)
9. [Limitations](#-limitings)
10. [Contributing & Star](#-contributing--star)

---

## 🎯 Purpose of This Project
Handwritten signature forgery is a prevalent security risk in banking, legal agreements, and administrative workflows. Traditional manual verification is slow, subjective, and prone to human error. 

The **AI-Powered Signature Verifier** automates this process by leveraging **Deep Learning (Siamese Neural Networks)**. It compares a newly uploaded test signature against a user's registered reference signature, extracts deep feature embeddings, calculates their cosine similarity, and renders a verified decision within seconds.

---

## 📂 Folder Structure
```text
signature_verifier/
│
├── app.py                      # Main Flask application & routes
├── requirements.txt            # Python dependencies
├── static/
│   └── uploads/                # Stores registered & temporary test signatures
├── templates/
│   ├── index.html              # Home dashboard displaying registered users
│   ├── register.html           # User registration form
│   ├── verify.html             # Signature verification upload interface
│   └── verify_result.html      # Results page with similarity scores & status
└── utils/
    ├── preprocessing.py        # Image processing, thresholding, and normalization
    ├── siamese.py              # Model loader, architecture, and verification logic
    └── siamese_signature_model.h5  # Pre-trained Siamese weights (or baseline fallback)

```

---

## 🏗️ Architecture Diagram

The system follows a Model-View-Controller (MVC)-inspired pattern integrated with a Deep Learning inference pipeline:

```text
 ┌───────────────┐        HTTP Request        ┌───────────────────────┐
 │  User Browser │ ──────────────────────────>│      Flask Server     │
 └───────────────┘                            └──────────┬────────────┘
         ▲                                               │
         │ Rendered HTML                                 ▼
         │                                    ┌───────────────────────┐
         └────────────────────────────────────│   Database (SQLite)   │
                                              └──────────┬────────────┘
                                                         │ Fetch Reference Path
                                                         ▼
                                              ┌───────────────────────┐
                                              │ utils/preprocessing   │
                                              └──────────┬────────────┘
                                                         │ Normalized Arrays
                                                         ▼
                                              ┌───────────────────────┐
                                              │ Siamese Neural Model  │
                                              └──────────┬────────────┘
                                                         │ Cosine Similarity
                                                         ▼
                                              ┌───────────────────────┐
                                              │  Match Result / Score │
                                              └───────────────────────┘

```

---

## 🔄 Data Flow Diagram (DFD)

### Level 1: Verification Flow

1. **Input:** User submits a `User ID` and a test signature image file via the `/verify` route.
2. **Storage:** Flask saves the image temporarily as `test_temp.png`.
3. **Retrieval:** The app queries SQLite to fetch the correct `signature_path` belonging to the selected user.
4. **Processing:** Both images are sent to `preprocessing.py` (Grayscale ➔ Otsu Thresholding ➔ Bounding Box Crop ➔ Resize to 220x155 ➔ Normalization).
5. **Inference:** Preprocessed arrays are passed to the Siamese network to generate 128-dimensional embedding vectors.
6. **Decision:** Cosine similarity is computed, scaled to a 0–100% score, evaluated against a 75% threshold, and displayed to the user.

---

## 📊 Entity-Relationship (ER) Diagram

The application utilizes a lightweight relational model managed through SQLAlchemy:

```text
       USER ENTITY
┌───────────────────────────┐
│ id (PK, Integer)          │
│ name (String, Not Null)   │
│ email (String, Unique)    │
│ signature_path (String)   │
└───────────────────────────┘

```

---

## 🚀 Installation & Setup Guide

### Prerequisites

* Python 3.8 or higher installed on your system.
* Git installed.

### Step 1: Clone the Repository

```bash
git clone [https://github.com/alok-kumar8765/advanced-qa-framework.git](https://github.com/alok-kumar8765/advanced-qa-framework.git)
cd advanced-qa-framework/signature_verifier

```

### Step 2: Create a Virtual Environment (Recommended)

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

```

### Step 3: Install Dependencies

Create or install the required dependencies:

```bash
pip install flask flask-sqlalchemy tensorflow opencv-python numpy werkzeug

```

### Step 4: Run the Application

```bash
python app.py

```

### Step 5: Access the Web App

Open your web browser and navigate to:

```text
[http://127.0.0.1:5000](http://127.0.0.1:5000)

```

---

## 💻 How to Use

1. **Register a User:**
* Click on **Register** from the home dashboard.
* Enter your **Name** and **Email**.
* Upload a clear, high-contrast image of your authentic signature and submit.


2. **Verify a Signature:**
* Go to the **Verify** tab.
* Select your registered name/ID from the dropdown list.
* Upload a test signature image (either a genuine match or an attempt at forgery).
* View the instant **Similarity Score percentage** and whether the system marks it as **Genuine** or **Forged**.



---

## ⚖️ Pros & Cons

### Pros

* **Automated & Fast:** Reduces verification time from minutes/hours to sub-seconds.
* **Smart Preprocessing:** Robust against background noise, paper shadows, and uneven margins due to Otsu thresholding and bounding-box cropping.
* **Extensible Architecture:** Built on Flask and TensorFlow, making it easy to scale or swap out with heavier state-of-the-art models (like ResNet backbones).
* **Graceful Fallback:** Automatically sets up a functional baseline CNN architecture if pre-trained weights are missing.

### Cons

* **Dataset Dependency:** Accuracy heavily depends on the training quality of the Siamese model weights.
* **Fixed Resolution Constraints:** Requires specific input formatting (220x155px), which can occasionally clip highly stylized or sprawling signatures.

---

## ⚠️ Limitations

* **Lighting & Angle Variations:** Extreme camera angles or heavy shadows on smartphone photos of signatures can still degrade accuracy despite pre-processing filters.
* **Single Reference Sample:** The current setup compares the test signature against a single registered reference image. Real-world systems typically require 3–5 reference samples to capture natural intra-personal signature variations.
* **CPU Inference Overhead:** Running TensorFlow inference on standard server CPUs without GPU acceleration can experience slight latency under heavy concurrent loads.

---

## ⭐ Contributing & Support

Contributions, issues, and feature requests are welcome!
If you find this project useful, please give it a **Star** ⭐ on GitHub!

* **GitHub Profile:** [@alok-kumar8765](https://github.com/alok-kumar8765)
