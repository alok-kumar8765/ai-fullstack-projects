<div align="center">

# 🎨 Cartoon Studio Creator API & Web App

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-005571.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red.svg)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Follow](https://img.shields.io/badge/GitHub-alok--kumar8765-lightgrey?logo=github)](https://github.com/alok--kumar8765)

*A production-grade, full-stack interactive cartoon creation studio powered by a Python FastAPI backend, SQLAlchemy persistence, AI background removal (`rembg`), and client-side Fabric.js canvas rendering.*

</div>

---

## 📋 Table of Contents
1. [Use & Purpose](#-use--purpose)
2. [Features](#-features)
3. [System Requirements](#-system-requirements)
4. [File Structure](#-file-structure)
5. [Installation & Setup](#-installation--setup)
6. [Data Flow Diagram (DFD)](#-data-flow-diagram-dfd)
7. [Entity-Relationship (ER) Diagram](#-entity-relationship-er-diagram)
8. [Pros & Cons](#-pros--cons)
9. [Limitations](#-limitations)
10. [Bugs & Vulnerabilities](#-bugs--vulnerabilities)
11. [Future Updates](#-future-updates)
12. [Contributing & Support](#-contributing--support)

---

## 🎯 Use & Purpose

### Purpose
The **Cartoon Studio Creator** bridges the gap between complex desktop vector software (like Adobe Illustrator or Photoshop) and lightweight web tools. It provides a seamless, browser-native canvas where users can compose characters, insert dynamic speech bubbles, manipulate layers, and export high-resolution assets instantly.

### Use Cases
* **Educational Tools:** Quickly generate storyboards and illustrated comic scripts for digital learning.
* **Content Creation:** Produce custom social media avatars, memes, and reaction graphics.
* **Developer Prototyping:** Serve as a boilerplate for custom image-composition web platforms backed by Python microservices.

---

## ✨ Features

* **Dynamic Asset Discovery:** Automatically scans the `static/assets/` directory and exposes any image file dynamically to the frontend UI without hardcoded mapping.
* **AI Background Removal (`rembg`):** Upload any raw image from your local device; the Python backend strips the background instantly and registers it as a transparent asset.
* **Interactive Canvas Engine:** Built with Fabric.js supporting object dragging, scaling, rotation, text editing, and z-index ordering.
* **Robust Persistence Layer:** Utilizes SQLAlchemy and SQLite/PostgreSQL to save canvas JSON states and high-resolution exported PNG snapshots.
* **High-Resolution Multiplier Export:** Renders canvas exports at $2\times$ scale for crisp Retina display outputs.

---

## 💻 System Requirements

* **Python:** `3.9` or higher
* **RAM:** Minimum 2GB (4GB recommended if running heavy `rembg` AI background removal models)
* **OS:** Windows, macOS, or Linux
* **Browser:** Any modern Chromium/Firefox/Safari browser with JavaScript enabled

---

## 📂 File Structure

```text
cartoon-creator/
├── main.py             # FastAPI entry point, routing, and static mounts
├── models.py           # SQLAlchemy database configuration and models
├── schemas.py          # Pydantic validation and serialization schemas
├── cartoons.db         # SQLite database file (auto-generated)
├── exports/            # Saved high-resolution PNG snapshots
├── static/
│   ├── fabric.min.js   # Local Fabric.js library fallback
│   └── assets/         # Dynamic asset repository (avatars, props, backgrounds)
└── templates/
    └── index.html      # Jinja2 frontend studio template & UI logic
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/alok--kumar8765/cartoon-creator.git
cd cartoon-creator
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv env
# On Windows:
env\Scripts\activate
# On macOS/Linux:
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy pydantic rembg pillow onnxruntime python-multipart jinja2
```

### 4. Initialize Asset Folders
Ensure your directory structure contains `static/assets/` and drop your initial transparent PNG characters inside.

### 5. Run the Application
```bash
uvicorn main:app --reload --port 8000
```

Open your browser and navigate to: **`http://127.0.0.1:8000`**

---

## 📊 Data Flow Diagram (DFD)

```text
 [ User Browser (HTML/JS + Fabric.js) ]
          │
          │ (1) HTTP GET /api/assets
          ▼
    [ FastAPI Backend ] ──(Scan)──► [ static/assets/ Folder ]
          │
          │ (2) HTTP POST /api/cartoons/save (Base64 PNG + JSON state)
          ▼
    ┌───────────┐         ┌────────────────────┐
    │  Decode   │ ──────► │ Save PNG to disk   │ ──► /exports/
    │  Base64   │         └────────────────────┘
    └───────────┘         ┌────────────────────┐
          │               │ Commit metadata    │ ──► cartoons.db (SQLAlchemy)
          ▼               └────────────────────┘
    [ Return JSON Response with image_url ]
```

---

## 📐 Entity-Relationship (ER) Diagram

```text
+-------------------------------------------------------+
|                       CARTOONS                        |
+-------------------------------------------------------+
| PK  | id           | VARCHAR (UUID)                   |
|     | title        | VARCHAR (NotNull)                |
|     | user_id      | VARCHAR (Default: 'guest')       |
|     | image_url    | VARCHAR (NotNull)                |
|     | canvas_json  | JSON (Stores Fabric object tree) |
|     | created_at   | DATETIME                         |
+-------------------------------------------------------+
```

---

## ⚖️ Pros & Cons

### Pros
* **Monolith Simplicity:** Combines Python backend logic and HTML templates into a single repository without complex Node.js/React build pipelines.
* **Extensible:** Easy to hook up additional AI pipelines (Stable Diffusion, Replicate) via FastAPI routers.
* **Zero Client Configuration:** CDN/Local static asset delivery means zero client-side setup required for end users.

### Cons
* **Monolithic Scaling:** Storing static files and SQLite on a single local server limits horizontal scaling without migrating to AWS S3 and PostgreSQL.
* **Rasterization Limits:** Canvas exports are raster PNGs rather than native scalable vector graphics (SVG).

---

## ⚠️ Limitations
* Maximum canvas resolution is bound by client browser memory during multi-layer composition.
* Concurrent AI background removal requests (`rembg`) on lower-spec hardware can introduce CPU bottlenecks.

---

## 🐛 Bugs & Vulnerabilities
* **Unsanitized Payload Size:** Large high-resolution base64 canvas strings lack strict payload body size limits, opening potential memory-exhaustion vectors if flooded.
* **Local File Overwrite Risk:** UUID generation mitigates collisions, but file cleanup routines are not yet implemented for deleted user drafts.

---

## 🔮 Future Updates
* [ ] **Cloud Storage Integration:** Migrate exported files from local disk to AWS S3 / Cloudinary.
* [ ] **Vector SVG Export:** Implement server-side vector rendering via `cairosvg`.
* [ ] **User Authentication:** Add JWT-based login and private user galleries.
* [ ] **AI Prompt Generator:** Direct integration with Replicate API for prompt-to-character generation.

---

## 🙏 Thanks & Star the Repo

If this project helped you learn or build something cool, please consider giving it a ⭐ on GitHub!

* **GitHub Profile:** [alok--kumar8765](https://github.com/alok--kumar8765)

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/alok--kumar8765/cartoon-creator/issues).