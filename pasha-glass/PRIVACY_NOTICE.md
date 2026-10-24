# Privacy Notice & Principles

## 1. Privacy First Architecture
PASHA-GLASS is designed ground-up as a privacy-preserving smart glasses context assistant.

### Key Safeguards:
- **No Public Facial Recognition:** Unknown faces detected in camera frames are NEVER identified against public social media or web search engines.
- **Default Face Blurring:** Any face that does not match an opt-in contact with high confidence (>= 0.85 cosine similarity) is automatically blurred on the local preview and HUD display.
- **Transient Frame Cache Auto-Deletion:** Unmatched video frames and face crops are automatically deleted from memory and temporary cache within 24 hours (or immediately after processing).
- **Private Data Sync Only:** Context information is sourced ONLY from the user's own private calendar (Google Calendar) and authorized CRM (HubSpot), NOT from public social media scraping.
- **On-Device Storage:** All database files (encrypted SQLite) and vector models (InsightFace / Qdrant Lite) run entirely on the user's companion smartphone device.

## 2. Technical Safeguards
- **Cosine Similarity Threshold:** Set to a strict `0.85` minimum threshold. Any score below `0.85` renders the person as `"Unknown person - no data"`.
- **Local SQLite Encryption:** Biometric embeddings and contact notes are stored using AES-256 encrypted fields.
- **BLE Stream Encrypted Payload:** Transmission between Ray-Ban Meta Glasses and the Android companion app is encrypted end-to-end via Bluetooth Low Energy (BLE).

## 3. Transparency & Rights
Users and subjects have total control over their local data:
- Full data wipe available via API endpoint `/api/v1/gallery/purge`.
- Real-time privacy status indicator on HUD preview.
