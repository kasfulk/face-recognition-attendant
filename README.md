# Face-Absen

**Face-Absen** is a self-hosted, privacy-centric Face Recognition Attendance System designed for local deployment. It replaces cloud-based biometric services with a robust, containerized solution that keeps all data within your private network.

Built with **FastAPI**, **InsightFace** (ArcFace), and **MediaPipe**, it offers enterprise-grade accuracy with real-time video-based liveness detection to prevent spoofing attacks.

![Badge](https://img.shields.io/badge/Status-MVP-success)
![Docker](https://img.shields.io/badge/Deployment-Docker-blue)
![Python](https://img.shields.io/badge/Backend-FastAPI-green)

---

## 🌟 Key Features

- **100% On-Premise**: No data is sent to external cloud APIs. Complete data sovereignty.
- **Anti-Spoofing (Liveness)**: Video-based challenge-response (Blink, Head Turn) using MediaPipe FaceMesh to defeat photo/screen attacks.
- **High Accuracy**: Uses state-of-the-art **ArcFace** (buffalo_l) models for face recognition.
- **Fast Vector Search**: Leverages **PostgreSQL + pgvector** for efficient 512-dimensional embedding storage and retrieval.
- **Containerized**: Zero-dependency deployment via Docker Compose.

## 🛠 Tech Stack

- **Backend**: Python 3.10, FastAPI, Uvicorn
- **AI Engine**: InsightFace (Recognition), MediaPipe (Liveness), OpenCV
- **Database**: PostgreSQL 15 with `pgvector` extension
- **Frontend**: Vanilla HTML/JS (Minimal MVP Kiosk)

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Webcam (for testing attendance)

### Installation

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/face-absen.git
    cd face-absen
    ```

2.  **Environment Setup**
    Copy the example environment file (optional, defaults allow running out-of-the-box):

    ```bash
    cp .env.example .env
    ```

3.  **Run with Docker**
    This command builds the backend image (installing system deps & Python packages) and starts the database.

    ```bash
    docker compose up --build
    ```

    _Note: The first run triggers a download of the InsightFace models (~300MB). Ensure internet connectivity._

4.  **Access the Application**
    - **Frontend Kiosk**: [http://localhost:8000/static/index.html](http://localhost:8000/static/index.html)
    - **Enrollment Page**: [http://localhost:8000/static/enroll.html](http://localhost:8000/static/enroll.html)
    - **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📖 Usage Guide

### 1. Enroll an Employee

1.  Navigate to `/static/enroll.html`.
2.  Enter an Employee ID (e.g., `EMP001`).
3.  Upload a clear photo of the employee's face.
4.  Click **Enroll**. The system generates a face embedding and stores it in the vector database.

### 2. Take Attendance

1.  Open the Kiosk at `/static/index.html`.
2.  Allow camera access.
3.  Click **Start Check-In**.
4.  **Liveness Challenge**: Follow the on-screen instruction (e.g., "BLINK" or "TURN LEFT").
5.  **Verification**: Once liveness is verified, the system matches the face against the enrolled database.
6.  **Success**: Access granted if confidence > 60%.

## 📂 Project Structure

```
face-absen/
├── app/
│   ├── api/            # API Route Handlers
│   ├── core/           # AI Engines (Face, Liveness)
│   ├── db/             # Database Models & Repositories
│   ├── templates/      # Frontend HTML Files
│   ├── main.py         # App Entrypoint
│   └── config.py       # Configuration
├── docker/
│   └── init.sql        # DB Initialization Script
├── docker-compose.yml  # Container Orchestration
├── Dockerfile          # Backend Image Definition
└── requirements.txt    # Python Dependencies
```

## 🛡 License

This project is open-source and available under the [MIT License](LICENSE).
