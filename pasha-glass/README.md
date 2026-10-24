# PASHA-GLASS: Privacy-First Context Assistant for Ray-Ban Meta Glasses

<p align="center">
  <strong>On-Device Biometrics | Mandatory Face Blurring | Zero Public Scraping</strong>
</p>

---

## 🚀 Overview

**PASHA-GLASS** is an enterprise-grade, privacy-first context assistant built for Ray-Ban Meta Glasses. It allows users to view real-time context cards (such as upcoming meeting details and client background) on their glasses HUD display **without compromising public privacy or building surveillance databases**.

---

## 🛡️ Core Privacy Safeguards

1. **NO Public Facial Recognition:**
   - Unknown faces detected in camera streams are **NEVER** identified against public social media (X, LinkedIn, Instagram) or web search engines.
2. **Default Face Blurring:**
   - Any face that does not match a locally stored, opt-in contact with high confidence ($\ge 0.85$ cosine similarity) is automatically blurred using on-device Gaussian blurring.
3. **Encrypted Opt-In Gallery (Max 50 Contacts):**
   - Users manually add contacts with explicit consent.
   - Vector embeddings (InsightFace) are stored locally in an AES-256 encrypted SQLite database (`pasha_glass_app.db`).
   - Hard limit of **50 contacts** enforced at database layer to prevent mass surveillance usage.
4. **Private Context Sync Only:**
   - Syncs exclusively with user's authorized Google Calendar and CRM (HubSpot), never public social accounts.
5. **24-Hour Transient Data Purge:**
   - Unmatched frame logs and transient processing caches are auto-deleted after 24 hours.

---

## 🏗️ Architecture & Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md): Technical breakdown of dual boundary isolation and face blurring pipeline.
- [CONSENT.md](CONSENT.md): Explicit opt-in biometric consent agreement.
- [PRIVACY_NOTICE.md](PRIVACY_NOTICE.md): User privacy notice and data handling policy.

---

## 🛠️ Quickstart

### 1. Install Dependencies
```bash
pip install fastapi uvicorn opencv-python pillow numpy cryptography httpx pytest
```

### 2. Run Privacy Demo
```bash
python pasha-glass/demo.py
```

### 3. Start Companion API & HUD Display Mock
```bash
uvicorn api.main:app --app-dir pasha-glass --port 8080 --reload
```
Open [http://localhost:8080/frontend/index.html](http://localhost:8080/frontend/index.html) in your browser to view the Ray-Ban Meta Glasses HUD stream.

### 4. Run Automated Test Suite
```bash
pytest pasha-glass/tests/ -v
```
