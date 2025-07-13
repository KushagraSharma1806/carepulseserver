# 🩺 CarePulse Backend (FastAPI)

This is the backend API for **CarePulse**, a remote health monitoring and AI-assisted healthcare system built with FastAPI and JWT authentication.

## 🚀 Features

- RESTful API for managing patient vitals
- JWT-based secure user authentication
- AI-powered symptom analysis
- Auto doctor assignment & appointment booking
- Real-time vitals updates via WebSocket
- Symptom-specialist mapping with fallback logic
- Background scheduler for auto-confirmation of pending appointments

## 🧰 Tech Stack

- **Python 3.10+**
- **FastAPI**
- **SQLAlchemy**
- **SQLite** (or switchable DB support)
- **APScheduler** for background scheduling
- **OpenAI-compatible AI analysis**

## 📦 Installation

```bash
git clone https://github.com/YOUR_USERNAME/carepulse-backend.git
cd carepulse-backend
pip install -r requirements.txt
