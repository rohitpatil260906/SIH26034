# VIDHICHECK — AI-Based Packaged Commodity Compliance Checker

[![SIH Problem Statement](https://img.shields.io/badge/SIH-Problem%20Statement%202024-purple.svg)](https://sih.gov.in)
[![Legal Metrology](https://img.shields.io/badge/Act-Legal%20Metrology%20(PCR)%202011-blue.svg)](https://consumeraffairs.nic.in)
[![Python](https://img.shields.io/badge/Backend-FastAPI%20%7C%20PyTorch%20%7C%20OpenCV-green.svg)](https://fastapi.tiangolo.com)
[![Frontend](https://img.shields.io/badge/Frontend-React%2018%20%7C%20TypeScript%20%7C%20Tailwind-purple.svg)](https://react.dev)
[![Tests](https://img.shields.io/badge/Tests-16%2F16%20Passing-brightgreen.svg)](https://docs.pytest.org)

**VIDHICHECK** is an end-to-end statutory compliance verification platform engineered for enforcement officers under the **Legal Metrology (Packaged Commodities) Rules, 2011** (Ministry of Consumer Affairs, Food and Public Distribution, Government of India).

The platform ingests real packaged commodity images, performs multi-stage optical quality assessment and computer vision preprocessing, extracts bilingual label text via OCR, parses structured declarations using a multi-provider AI/LLM layer, runs an offline ML classification cascade, and validates all declarations against a deterministic, statutory Legal Metrology rule engine.

---

## 1. System Architecture

```
[ Uploaded Package Image (Front / Side / Back) ]
                       ↓
[ OpenCV Quality Assessment & CV Preprocessing Engine ]
    ├── 12 Optical Quality Metrics (Resolution, Blur, Noise, Glare, Skew)
    └── 13 Statutory Preprocessing Variants (Adaptive Threshold, CLAHE, Denoised...)
                       ↓
[ Optical Character Recognition (OCR) Engine ]
    ├── Bilingual Hindi + English EasyOCR (Primary)
    └── Tesseract OCR Engine (Failover / Client Augmentation)
                       ↓
[ AI / LLM Structured Extraction Layer ] (Provider Abstraction)
    ├── Google Gemini / OpenAI / Ollama (Configurable via ENV)
    └── Deterministic Offline NLP Fallback (Regex + Legal Metrology Heuristics)
                       ↓
[ Machine Learning (ML) Classification Service ]
    ├── Declaration Classifier (Token-level category tagging)
    ├── Product Category Classifier (Food, Cosmetics, Electronics, Medical)
    └── Risk & Confidence Module (Enforcement priority scoring)
                       ↓
[ Deterministic Legal Metrology (PCR 2011) Rule Engine ]
    ├── Rule 6(1)(a): Manufacturer / Packer / Importer Name & Complete Address
    ├── Rule 6(1)(b): Generic or Common Name of Commodity
    ├── Rule 6(1)(c): Net Quantity in Standard SI Units (Rule 7 compliance)
    ├── Rule 6(1)(d): Maximum Retail Price (MRP) + "incl. of all taxes"
    ├── Rule 6(1)(e): Month and Year of Manufacture / Packaging / Import
    ├── Rule 6(1)(f): Consumer Care Officer Details (Phone & Email)
    ├── Rule 5 / First Schedule: Unit Sale Price (USP) Calculation
    └── Optical Height & Legibility Estimation (First Schedule Rule 5 Table)
                       ↓
[ SQLite Statutory Persistence Layer ]
    ├── Case Dockets with Evidence Snapshots & Raw Transcripts
    └── Real-time Aggregated Dashboard Analytics
                       ↓
[ React + TypeScript Enforcement Portal ]
    ├── Live Camera Capture & Multi-surface Upload
    ├── Evidence Viewer with Bounding Boxes & Preprocessing Toggles
    ├── Statutory Inspection Docket Generator (Formal Legal Notice / Seizure Memo)
    └── Historical Inspection Docket Archive & Search
```

---

## 2. Key Features

1. **Deterministic Rule Engine (No Fake AI Compliance)**:
   - Compliance decisions are **never** left to generative LLM hallucinations.
   - 30+ statutory rules directly codified from the Legal Metrology Act, 2009 and PCR 2011.
   - Clear evidence trails with exact line-level references, expected requirements, and legal citations.

2. **Multi-Provider AI Extraction Architecture**:
   - Pluggable `AIProvider` base interface supporting Google Gemini, OpenAI, self-hosted Ollama, or local offline regex NLP.
   - Robust JSON schema validation ensuring fail-safe execution even in disconnected environments.

3. **Bilingual OCR & Image Preprocessing Pipeline**:
   - Evaluates 12 image quality dimensions before processing (blur Laplacian variance, contrast std dev, glare percentage).
   - Generates 13 statutory preprocessing variants for edge enhancement, glare suppression, and optimal character recognition.
   - Supports Devanagari (Hindi) and Latin (English) scripts.

4. **Statutory Persistence & Real-time Metrics**:
   - Automatically saves inspection dockets to SQLite (`backend/data/vidhicheck.db`).
   - Generates formal legal notices and seizure reports.
   - Live dashboard metrics reflecting real scan history, pass rates, and common violations.

5. **Government-Tech UI with Purple Theme**:
   - Preserves official portal styling with the statutory purple accent (`#7C3AED`).
   - Sticky click-to-toggle navigation dropdowns.
   - Accessible keyboard navigation and responsive layouts.

---

## 3. Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | React 18, TypeScript, Tailwind CSS, Vite, Lucide Icons | Responsive portal with camera capture, image editor, interactive docket view |
| **Backend API** | Python 3.10+, FastAPI, Uvicorn, Pydantic v2 | High-performance asynchronous REST API |
| **Database** | SQLite, SQLAlchemy ORM | Auto-migrating relational schema for case dockets and inspection records |
| **Computer Vision** | OpenCV (`cv2`), Pillow, NumPy | 12 quality metrics, 13 preprocessing variants, skew/glare detection |
| **OCR** | EasyOCR, PyTesseract | Bilingual English/Hindi extraction with bounding box geometry |
| **AI / LLM** | Google Gemini / OpenAI / Ollama / Local NLP | Standardized `AIProvider` contract with JSON validation |
| **Testing** | Pytest, FastAPI TestClient | 16 automated end-to-end and modular unit tests |

---

## 4. Getting Started & Installation

### Prerequisites
- **Node.js** (v18.x or higher)
- **Python** (v3.10 or higher)
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/vidhicheck.git
cd Vidhicheck--/SIH26034
```

### 2. Configure Environment Variables
Copy `.env.example` to create your local `.env`:
```bash
cp .env.example .env
```

Key environment options:
```ini
# Database
DATABASE_URL=sqlite:///./backend/data/vidhicheck.db

# LLM Configuration
LLM_PROVIDER=configurable
LLM_API_KEY=your_gemini_or_openai_key_here  # Leave blank for offline NLP fallback
LLM_MODEL=gemini-1.5-flash

# OCR Configuration
OCR_PROVIDER=easyocr

# Security
JWT_SECRET=supersecret-vidhicheck-jwt-signing-key
```

### 3. Backend Setup
```bash
# Navigate to the project root
cd SIH26034

# Install Python dependencies
pip install -r backend/requirements.txt

# (Optional) Pre-generate test image samples
python backend/generate_test_samples.py

# Start the FastAPI backend server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API documentation will be available at: `http://127.0.0.1:8000/docs`

### 4. Frontend Setup
In a separate terminal:
```bash
cd SIH26034

# Install frontend dependencies
npm install

# Start the Vite development server
npm run dev
```
The application will launch at: `http://localhost:5173`

---

## 5. Automated Testing

VIDHICHECK includes a test suite covering the entire pipeline from image quality analysis to API responses.

To execute all tests:
```bash
python -m pytest backend/test_pipeline.py -v
```

### Test Coverage Summary:
- `test_image_quality_sharp_vs_blurry`: Validates Laplacian variance, glare detection, and quality scores.
- `test_preprocessing_variants_generation`: Verifies creation of all 13 CV variants.
- `test_nlp_fallback_provider_extraction`: Verifies regex extraction of MRP, Net Qty, USP, Dates, and Consumer Care.
- `test_ai_provider_factory`: Ensures proper fallback and provider selection.
- `test_ml_declaration_classifier`: Verifies ML classification of label text chunks.
- `test_ml_product_category_classifier`: Verifies detection of Food, Cosmetic, Electrical, and Medical items.
- `test_ml_risk_confidence_module`: Verifies enforcement risk scoring.
- `test_rule_engine_compliant_package`: Validates clean pass on compliant commodities.
- `test_rule_engine_prohibited_units_violation`: Catches non-SI units (e.g. `gms` instead of `g`).
- `test_rule_engine_missing_mrp_tax_phrase`: Flags MRP missing "(inclusive of all taxes)".
- `test_database_crud_operations`: Validates SQLite CRUD for case dockets and reports.
- `test_api_system_status`: Verifies `/api/system/status` health check.
- `test_api_rules_list`: Verifies `/api/rules` statutory rule catalog.
- `test_api_dashboard_stats`: Verifies `/api/dashboard/stats` real-time metrics.
- `test_api_scans_and_reports_endpoints`: Verifies report saving, listing, retrieval, and deletion.
- `test_api_scan_process_end_to_end`: Tests full image upload, OCR, extraction, and rule evaluation.

---

## 6. REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/scan/process` | Ingests package images, runs CV/OCR/AI/Rules, and returns inspection docket |
| `GET` | `/api/scans` | Retrieves recent scan sessions |
| `GET` | `/api/reports` | Returns list of all persisted case dockets from SQLite |
| `POST` | `/api/reports` | Saves an inspection case docket to the statutory database |
| `GET` | `/api/reports/{id}` | Retrieves full inspection docket details by scan ID |
| `DELETE` | `/api/reports/{id}` | Deletes an inspection record |
| `GET` | `/api/dashboard/stats` | Calculates real-time metrics (total scans, compliance rate, violations) |
| `GET` | `/api/rules` | Catalogs all verified Legal Metrology (PCR 2011) statutory rules |
| `GET` | `/api/system/status` | Diagnostic health status of CV, OCR, AI, and Database subsystems |

---

## 7. Legal Metrology (PCR 2011) Rules Codified

| Rule ID | Statutory Reference | Requirement Verified |
|---|---|---|
| `PCR-R06-MFG-NAME` | Rule 6(1)(a) | Name and complete address of manufacturer, packer, or importer with valid PIN code |
| `PCR-R06-GENERIC-NAME` | Rule 6(1)(b) | Generic or common name of the commodity |
| `PCR-R06-NET-QTY` | Rule 6(1)(c) & Rule 7 | Net quantity in standard SI units (`g`, `kg`, `ml`, `l`). Prohibits `gms`, `litres`, etc. |
| `PCR-R06-MRP` | Rule 6(1)(d) | Maximum Retail Price clearly printed with "inclusive of all taxes" |
| `PCR-R06-DATE` | Rule 6(1)(e) | Month and Year of manufacture, packing, or import |
| `PCR-R06-CONSUMER-CARE` | Rule 6(1)(f) | Officer contact info: phone number, email address, and physical address |
| `PCR-R06-ORIGIN` | Rule 6(1)(aa) | Country of origin for imported goods |
| `PCR-R05-USP` | Rule 5 & 1st Schedule | Unit Sale Price (USP) per gram/millilitre for packages > 1 kg/litre or ≤ 1 kg/litre |
| `PCR-R05-CHAR-HEIGHT` | First Schedule Table | Minimum character height based on net quantity volume/weight |

---

## 8. Troubleshooting

1. **EasyOCR downloading models on first run**:
   - On the initial run, EasyOCR downloads language models (`~100MB`) to `~/.EasyOCR/`. If your system is offline or behind a strict firewall, the system gracefully falls back to Tesseract OCR and local NLP heuristics.

2. **Port 8000 already in use**:
   - Change the port in your terminal command: `python -m uvicorn backend.main:app --port 8001` and update `.env` with `PORT=8001`.

3. **Database locked or reset**:
   - The SQLite database is stored at `backend/data/vidhicheck.db`. You can safely delete or recreate it anytime; tables auto-migrate on backend start.

---

## 9. License

Developed for the Smart India Hackathon (SIH) — Legal Metrology Statutory Compliance Division.
All rules derived from the *Legal Metrology Act, 2009* and *Legal Metrology (Packaged Commodities) Rules, 2011*.
