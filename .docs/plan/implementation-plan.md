# Face-Absen — Implementation Guide

Dokumen ini merangkum **seluruh implementasi sistem absensi wajah** dari level produk sampai teknis, siap dipakai sebagai **blueprint implementasi & handover tim**.

---

## 1. Overview

**Face-Absen** adalah sistem absensi karyawan berbasis **Face Recognition + Video-based Liveness Detection** yang berjalan **on‑prem / private**, tanpa ketergantungan cloud eksternal.

### Tujuan utama

* Absensi cepat & akurat
* Anti kecurangan (foto / video replay)
* Mudah di-deploy (Docker)
* Mudah di-scale

---

## 2. Arsitektur Sistem

```text
Browser (Camera / Video)
   ↓
FastAPI Backend
   ├─ Liveness Engine (video-based)
   ├─ Face Recognition (InsightFace / ArcFace)
   ↓
PostgreSQL + pgvector
   ↓
Attendance Result
```

---

## 3. Technology Stack

| Layer            | Teknologi                         |
| ---------------- | --------------------------------- |
| Backend API      | FastAPI (Python)                  |
| Face Recognition | InsightFace (ArcFace – buffalo_l) |
| Liveness         | MediaPipe FaceMesh + OpenCV       |
| Vector DB        | PostgreSQL + pgvector             |
| Frontend         | HTML + JS (Web Camera)            |
| Deployment       | Docker + Docker Compose           |

---

## 4. Core Features

### MVP Features

* Enroll wajah karyawan (upload foto)
* Absensi via kamera browser
* Face vectorization (512-dim)
* Cosine similarity matching
* Attendance logging

### Security Features

* Video-based liveness detection
* Random challenge (blink / head turn)
* Time-bound verification

---

## 5. Folder Structure

```
face-absen/
│
├── app/
│   ├── main.py              # FastAPI routes
│   ├── face_engine.py       # InsightFace ArcFace
│   ├── liveness_engine.py   # Video-based liveness
│   ├── db.py                # PostgreSQL + pgvector
│   └── templates/
│       ├── upload-foto.html # Enroll UI
│       └── absen.html       # Absensi UI
│
├── docker/
│   └── init.sql             # pgvector + schema
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── implementation.md
```

---

## 6. Database Design

### Extensions

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Tables

```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    embedding VECTOR(512) NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);
```

### ERD (Logical)

```
employees (1) ──────── (N) attendance
```

---

## 7. Face Recognition

* Model: **InsightFace ArcFace (buffalo_l)**
* Output: **512-dim normalized embedding**
* Metric: **Cosine similarity**
* Threshold absensi: **≥ 0.6**

Flow:

```
Image → Face Detection → Embedding → Vector Search → Match
```

---

## 8. Video-based Liveness Detection

### Konsep

Challenge–response **real-time** menggunakan video stream.

### Challenge yang didukung

* BLINK (kedip)
* TURN_LEFT
* TURN_RIGHT
* (extensible)

### Flow

1. Backend generate challenge
2. Client stream frame (2–5 detik)
3. Backend analisis landmark wajah
4. Challenge terpenuhi → PASS

### Proteksi yang didapat

* Anti foto cetak
* Anti replay image
* Sulit pakai video rekaman

---

## 9. API Specification (OpenAPI)

### POST `/enroll`

Enroll wajah karyawan

**Request (multipart/form-data)**

* user_id: string
* image: file

**Response**

```json
{ "status": "enrolled", "user_id": "EMP001" }
```

---

### POST `/liveness/start`

Mulai sesi liveness

**Response**

```json
{ "session_id": "uuid", "challenge": "TURN_LEFT" }
```

---

### POST `/liveness/frame`

Upload frame video

**Request**

* session_id
* image (JPEG frame)

---

### POST `/liveness/verify`

Validasi liveness

**Response**

```json
{ "liveness": true }
```

---

### POST `/absen`

Absensi final (liveness + face recognition)

**Response (success)**

```json
{ "absen": true, "user_id": "EMP001", "confidence": 0.87 }
```

---

## 10. Web Interface

### Enroll UI (`/enroll-ui`)

* Input user_id
* Upload foto wajah
* Submit ke API `/enroll`

### Absensi UI (`/`)

* Kamera aktif
* Challenge ditampilkan
* Frame dikirim berkala
* Status absensi realtime

---

## 11. Docker Deployment

### Services

* api: FastAPI + InsightFace
* db: PostgreSQL + pgvector

### Run

```bash
docker compose up --build
```

Access:

* App: [http://localhost:8000](http://localhost:8000)
* Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 12. Performance Notes

* CPU-only OK untuk ≤ 1.000 karyawan
* Frame rate liveness: 300–500 ms
* Embedding cacheable

---

## 13. Roadmap (Next Phase)

### Phase 2

* Multi embedding per karyawan
* Admin auth & RBAC
* Attendance report (CSV/PDF)

### Phase 3 (Enterprise)

* CNN anti-spoof (SilentFace / FASNet)
* RTSP CCTV support
* Edge offline sync (Jetson / NPU)
* Audit log & compliance

---

## 14. Positioning

✔ Cocok untuk kantor, pabrik, pesantren, instansi
✔ Private & on‑prem
✔ Tidak vendor lock‑in
✔ Siap dikembangkan ke enterprise

---

**End of implementation.md**
