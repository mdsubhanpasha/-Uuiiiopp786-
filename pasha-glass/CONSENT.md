# Explicit Opt-In Consent & Verification Protocol

## Overview
PASHA-GLASS operates under a strict **Zero-Trust Privacy & Consent Architecture**. Under no circumstances will any individual's facial biometric features be processed, recognized, or stored without explicit, prior, written/digital opt-in consent from that individual.

## Consent Requirements
To register a person into the local **Opt-In Face Gallery**, the following mandatory consent criteria must be satisfied:

1. **Explicit Affirmative Opt-In:**
   - The individual must actively sign or acknowledge an opt-in form permitting biometric feature embedding extraction for local recognition on the user's Ray-Ban Meta Glasses.

2. **Strict Purpose Limitation:**
   - Biometric embeddings are strictly used for displaying context cards (e.g., meeting notes, previous client interactions) on the user's private HUD display.
   - Embeddings are NEVER shared, sold, uploaded to third-party APIs, or used for surveillance.

3. **Data Storage & Encryption:**
   - Biometric representations (InsightFace 512-d feature vectors) are encrypted using AES-256 and stored exclusively in the local, on-device SQLite database.
   - Vector embeddings cannot be reversed into original face photographs.

4. **Right to Revocation & Erasure:**
   - Any opt-in contact may request removal at any time.
   - Deleting a contact instantly wipes their record, photo, and embedding vector from the local database.

5. **Strict Capacity Limit:**
   - The opt-in gallery enforces a hard limit of **50 contacts**. Mass identification or broad population scanning is technically restricted by design.

---
*By maintaining an opt-in gallery, PASHA-GLASS respects individual privacy rights, complying with GDPR Article 9 (Special Categories of Data / Biometric Data) and CCPA / BIPA regulations.*
