# PASHA-GLASS Technical Architecture & Privacy Engineering

## Abstract
Ray-Ban Meta Glasses present a unique paradigm for Augmented Reality (AR) HUD displays. However, unconstrained facial recognition poses severe ethical and privacy risks. PASHA-GLASS implements an enterprise-grade, privacy-first context engine designed specifically to eliminate public facial recognition, mass surveillance, and unauthorized profiling.

---

## 1. Architectural Safeguards: Why We Ban Public Facial Recognition

### The Threat of Public Facial Recognition
Public facial recognition (scraping web photos, LinkedIn, X, Instagram, or clearview-style databases) destroys individual anonymity in public spaces, enables stalkerware, and violates basic human rights laws (GDPR Art 9, CCPA, Illinois BIPA).

### PASHA-GLASS Architectural Solution
PASHA-GLASS introduces **Dual Boundary Isolation**:

```
[ Glasses BLE Stream ] ---> [ On-Device Face Detector ]
                                    |
                    +---------------+---------------+
                    |                               |
          (Face Detected)                   (No Face / Unknown)
                    |                               |
   [ Extract 512-d Embedding ]           [ Apply Heavy Gaussian Blur ]
                    |                               |
    [ Compare against Local Gallery ]               |
            (Threshold >= 0.85)                     v
        +-----------+-----------+        [ Render "Unknown Person - No Data" ]
        |                       |        [ Auto-delete frame within 24h ]
     (Match)                (No Match)
        |                       |
  [ Fetch Private CRM ]         +---> [ Apply Blur & Show "Unknown" ]
  [ Show Context Card ]
```

1. **Closed-Loop Matching:** Feature vectors extracted by InsightFace are ONLY compared against an on-device local gallery (hard-coded limit of 50 contacts).
2. **No External Network Calls for Biometrics:** Vector comparison happens in local memory (or Qdrant Lite embedded mode). No vector is ever transmitted over HTTP/Cloud.
3. **Opt-In Only:** A contact vector exists in the database ONLY if the contact explicitly provided consent and photo upload via the companion app.
4. **Immediate Fallback:** If cosine similarity is `< 0.85`, the system immediately classifies the face as `Unknown`, applies Gaussian blurring over the region of interest, and outputs `"Unknown person - no data"`.

---

## 2. Component Pipeline

1. **BLE Video Ingestion:** Receives raw camera frame buffer over encrypted BLE companion channel.
2. **On-Device Face Detector:** Runs lightweight RetinaFace / Haar / HOG detector on device CPU/NPU.
3. **Face Blurring Engine:** Applies OpenCV Gaussian Blur (`ksize=(51,51), sigma=30`) over bounding box coordinates for all unverified faces.
4. **Local Vector Engine:** Calculates 512-dimensional embedding normalized vector. Cosine similarity score $S$:
   $$S(u, v) = \frac{u \cdot v}{\|u\| \|v\|}$$
5. **Private Context Integrator:** Syncs with user's Google Calendar & HubSpot CRM to fetch meeting notes and mutual context.
6. **Glasses HUD Display Overlay:** Renders non-intrusive card on Ray-Ban Meta Glasses HUD overlay.

---

## 3. Compliance & Auditability
- **Audit Logs:** System logs biometric evaluation events without saving face images.
- **24-Hour Cache Purge:** Background scheduler sweeps transient frame cache and removes any temporary data older than 24 hours.
