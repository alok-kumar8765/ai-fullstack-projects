# 🛡️ Advanced AI-Powered Signature Verifier (Multi-Sample & GPU Support)

> An enterprise-grade, secure, and robust web application built with **Flask**, **TensorFlow/Keras**, and **OpenCV** to authenticate and verify handwritten signatures using **Siamese Neural Networks** with multi-sample enrollment and REST API support.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?style=for-the-badge&logo=flask&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?style=for-the-badge&logo=tensorflow&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
[![GitHub Owner](https://img.shields.io/badge/GitHub-alok--kumar8765-lightgrey?style=for-the-badge&logo=github)](https://github.com/alok-kumar8765)

---

## 📋 Table of Contents
1. [Purpose of This Project](#-purpose-of-this-project)
2. [Key Features & Upgrades](#-key-features--upgrades)
3. [Folder Structure](#-folder-structure)
4. [Architecture Diagram](#-architecture-diagram)
5. [Data Flow Diagram (DFD)](#-data-flow-diagram-dfd)
6. [Entity-Relationship (ER) Diagram](#-entity-relationship-er-diagram)
7. [Installation & Setup Guide](#-installation--setup-guide)
8. [How to Use & Test the API](#-how-to-use--test-the-api)
9. [Pros & Cons](#-pros--cons)
10. [Limitations](#-limitations)
11. [Contributing & Star](#-contributing--star)

---

## 🎯 Purpose of This Project
Handwritten signature forgery remains a major security vulnerability across banking, legal contracts, and enterprise documentation workflows. Traditional manual verification is slow, subjective, and vulnerable to fatigue or visual oversight.

This project automates biometric signature verification by deploying **Siamese Convolutional Neural Networks (CNN)**. Unlike basic prototypes, this advanced build supports **multi-sample reference profiling** (accounting for natural variations in human handwriting) and provides a **versioned REST API (`/api/v1/...`)** alongside a responsive Bootstrap 5 web interface.

---

## 🚀 Key Features & Upgrades
* **Multi-Sample Enrollment:** Users can upload multiple reference variations (3–5 signatures) during registration, drastically lowering false-positive forgery alerts caused by natural writing inconsistencies.
* **Max-Match Confidence Scoring:** Compares test signatures against *all* stored reference samples for a user and evaluates the highest similarity percentage.
* **Versioned REST API Endpoints:** Built-in JSON endpoints (`/api/v1/users`, `/api/v1/verify`) enabling external mobile apps or web portals to consume the verification engine asynchronously.
* **Smart OpenCV Preprocessing:** Automated grayscale conversion, Otsu binarization, bounding-box cropping (whitespace removal), and pixel normalization.
* **GPU Memory Growth Management:** Automatically detects available physical CUDA GPUs and configures dynamic VRAM growth.

---

## 📂 Folder Structure
```text
signature_verifier/
│
├── app.py                      # Core Flask app, DB models, UI routes & Versioned REST APIs
├── requirements.txt            # Python dependencies
├── test_api.py                 # Automated testing script using the requests library
├── static/
│   └── uploads/                # Secure destination for registered and temporary test files
├── templates/
│   ├── index.html              # Dashboard showing users and enrollment sample counts
│   ├── register.html           # Multi-file batch signature enrollment form
│   ├── verify.html             # Multi-sample verification upload UI
│   └── verify_result.html      # Detailed metrics view with confidence progress bar
└── utils/
    ├── __init__.py
    ├── preprocessing.py        # Image cleaning, Otsu thresholding, bounding box & normalization
    ├── siamese.py              # GPU configuration, CNN architecture & cosine similarity engine
    └── siamese_signature_model.h5  # Pre-trained Siamese weights (or runtime fallback skeleton)

```

---

## 🏗️ Architecture Diagram

```text
 ┌───────────────┐        HTTP Request        ┌───────────────────────┐
 │  User Browser │ ──────────────────────────>│      Flask Server     │
 └───────────────┘                            └──────────┬────────────┘
         ▲                                               │
         │ Rendered HTML                                 ▼
         │                                    ┌───────────────────────┐
         └────────────────────────────────────│   Database (SQLite)   │
                                              └──────────┬────────────┘
                                                         │ Fetch All Sample Paths
                                                         ▼
                                              ┌───────────────────────┐
                                              │ utils/preprocessing   │
                                              └──────────┬────────────┘
                                                         │ Normalized Arrays
                                                         ▼
                                              ┌───────────────────────┐
                                              │ Siamese Neural Model  │
                                              └──────────┬────────────┘
                                                         │ Max Cosine Similarity
                                                         ▼
                                              ┌───────────────────────┐
                                              │  Match Result / Score │
                                              └───────────────────────┘

```

---

## 🔄 Data Flow Diagram (DFD)

1. **Enrollment Input:** User submits `name`, `email`, and a batch of reference signature files via `/register`.
2. **Database Mapping:** A `User` record is created, establishing a **One-to-Many relationship** with multiple `SignatureSample` records.
3. **Verification Input:** User uploads a test signature file via the `/verify` or `/api/v1/verify` endpoint.
4. **Batch Comparison Pipeline:** The app loops through *every* reference sample linked to that user, running preprocessing and embedding predictions.
5. **Decision & Output:** The highest similarity percentage is evaluated against the 75% security threshold and rendered.

---

## 📊 Entity-Relationship (ER) Diagram

The relational database utilizes a clean One-to-Many schema managed via Flask-SQLAlchemy:

```text
       USER ENTITY                         SIGNATURE SAMPLE ENTITY
┌───────────────────────────┐         ┌───────────────────────────────┐
│ id (PK, Integer)          │ 1     N │ id (PK, Integer)              │
│ name (String, Not Null)   │─────────│ user_id (FK -> user.id)       │
│ email (String, Unique)    │         │ filepath (String, Not Null)   │
└───────────────────────────┘         └───────────────────────────────┘

```

---

## 🚀 Installation & Setup Guide

### Prerequisites

* Python 3.8+ installed on your system.
* Git installed.

### Step 1: Clone the Repository

```bash
git clone [https://github.com/alok-kumar8765/advanced-qa-framework.git](https://github.com/alok-kumar8765/advanced-qa-framework.git)
cd advanced-qa-framework/signature_verifier

```

### Step 2: Create & Activate Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt

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

## 💻 How to Use & Test the API

### 1. Web Interface

* **Register:** Go to `/register`, input name/email, and hold `Ctrl`/`Cmd` to select multiple reference signature samples (3–5 recommended).
* **Verify:** Go to `/verify`, select the registered user profile, upload a test sample, and view the confidence score.

### 2. Automated API Testing Script

You can test both the multi-sample registration and versioned REST API endpoints programmatically using the included test script:

```bash
python test_api.py

```

---

## ⚖️ Pros & Cons

### Pros

* **Higher Accuracy:** Multi-sample enrollment accounts for natural writing variations.
* **REST API Ready:** Versioned endpoints (`/api/v1/...`) allow seamless integration with external clients.
* **Robust Preprocessing:** Isolated line binarization and bounding-box cropping ensure robustness against environmental shadows.
* **Hardware Flexible:** Gracefully handles CPU fallback while supporting GPU memory growth.

### Cons

* **Model Training Overhead:** Achieving high-precision verification requires a well-trained custom Siamese weights file (`.h5`).
* **Storage Footprint:** Storing multiple reference samples per user consumes more server disk space compared to single-image models.

---

## ⚠️ Limitations

* **Lighting Variations:** Extreme shadows or blurry smartphone photos can occasionally degrade binarization quality.
* **Inference Latency on CPU:** Running heavy deep learning matrix multiplications on standard server CPUs without a dedicated GPU can introduce slight delays under heavy request traffic.

---

## ⭐ Contributing & Support

Contributions, issues, and feature requests are welcome! If you find this project helpful, please give it a **Star** ⭐ on GitHub!

* **GitHub Profile:** [@alok-kumar8765](https://github.com/alok-kumar8765)











































Haan, bilkul! Is project ko aur zyada powerful, secure, aur industry-ready banane ke liye aap isme kayi saare **advanced features** add kar sakte hain.

Aapke project ke current scope ke hisab se ye kuch best features hain jo aap step-by-step add kar sakte hain:

---

### 1. **Signature Canvas / Drawing Pad (No Upload Required)**

* **Kaise Kaam Karega:** Abhi users ko signature ki image upload karni padti hai. Aap isme HTML5 Canvas (`<canvas>`) jodh sakte hain jisse user mouse, stylus, ya phone ki touch screen par direct sign kar sake.
* **Benefit:** User experience bahut smooth ho jata hai aur file upload karne ki jhanjhat khatam ho jati hai.

### 2. **Verification Audit Trail & History Logs**

* **Kaise Kaam Karega:** Ek naya database table (`AuditLog`) banayein jo har verification attempt ka data store kare—jaise:
* Kis user ko check kiya gaya
* Test signature ki file ka path
* Similarity score kitna aaya (`85%`, `40%`, etc.)
* Status kya tha (`Genuine` ya `Forged`)
* Timestamp (kis tareek aur samay par check hua)


* **Benefit:** Banking ya legal systems mein audit trail hona zaroori hota hai taaki pata chal sake kisne kab verification kiya tha.

### 3. **Liveness / Anti-Spoofing Detection (Screen Capture Check)**

* **Kaise Kaam Karega:** Kai baar log kisi computer screen ya printed paper ki photo kheech kar upload kar dete hain. Aap OpenCV ki madad se image mein screen moiré patterns (pixel grid lines) ya print halftone dots ko detect karne ka logic laga sakte hain.
* **Benefit:** System ki security high-level ho jayegi aur koi fake photo se bypass nahi kar payega.

### 4. **Grad-CAM / Heatmap Visualization (Explainable AI)**

* **Kaise Kaam Karega:** Jab AI model signature ko verify kare, toh ek heatmap generate kare jo ye dikhaye ki model ne signature ke kis hisse (jaise loops, strokes, ya dots) ko dekh kar match kiya ya forgery declare kiya.
* **Benefit:** User ko exact reason dikhega ki kyu signature match nahi hua (jaise: *"Stroke mismatch in second letter"*).

### 5. **Admin Dashboard & Role-Based Access Control (RBAC)**

* **Kaise Kaam Karega:** Flask-Login ya JWT authentication ka use karke roles banayein:
* **User:** Apne signatures register aur verify kar sake.
* **Admin:** Saare users ko manage kar sake, threshold value (`0.75` se `0.80`) ko UI se change kar sake, aur logs dekh sake.


* **Benefit:** Real-world enterprise applications ke liye ye mandatory feature hai.

### 6. **Multi-Factor Thresholding (Dynamic Threshold)**

* **Kaise Kaam Karega:** Abhi threshold fix hai (`0.75`). Aap aisa system bana sakte hain jisme user ke signature ki complexity ke hisab se threshold dynamically adjust ho (kuch logon ke signature bahut simple hote hain, kuch ke complex).

---

Aap inmein se kis feature ko sabse pehle implement karna chahenge? Main aapko uska complete code aur implementation guide de sakta hoon!