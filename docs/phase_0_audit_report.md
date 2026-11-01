# Phase 0 Audit Report: Campus AI Project

**Date:** 2026-10-26  
**Auditor:** Anjali Upadhyay, Diya Rajpal, Lakshya Gupta  
**Scope:** Repository inventory, baseline model verification, gap analysis, and architectural plan.

---

## 1. Executive Summary

Campus AI is an NLP-powered student campus assistant designed to ingest, classify, prioritize, and extract actionable information from college communications (such as exams, timetable shifts, and deadlines), exposing these capabilities through a FastAPI backend to an Android mobile application and Notion workspace.

An audit of the workspace reveals:
1. **NLP Foundation (Person 1):** A mature, verified NLP inference pipeline exists in [`NLP PROJECT/campusai_artifacts`]. The unit tests pass 100% (12/12 tests in 2.6s).
2. **Backend & Database:** No backend services or database schemas currently exist. These will be constructed in [`CAMPUS AI/backend`] using **FastAPI**, **Pydantic v2**, and **SQLAlchemy/Alembic** for PostgreSQL.
3. **Android Client:** No mobile application code exists in the workspace yet. The complete Android client architecture (Java/XML) will be scaffolded in 

---

## 2. Inventory of Existing NLP Assets (Person 1)

Located in: [`NLP PROJECT/campusai_artifacts/`]

### 2.1 Model Artifacts (`models/`)
| Artifact File | Role in Pipeline | Classes / Features |
|---|---|---|
| [`category_logreg_tfidf.joblib`] | Category Classifier | 12 classes (`ACADEMIC`, `ADMINISTRATIVE`, `ASSIGNMENT`, `ATTENDANCE`, `CLASSROOM / TIMETABLE`, `EVENT`, `EXAM`, `FEES`, `GENERAL`, `PLACEMENT`, `REGISTRATION`, `WORKSHOP`) |
| [`tfidf_vectorizer.joblib`] | TF-IDF for Category Model | Text unigrams/bigrams on cleaned email text |
| [`sender_role_onehot.joblib`]| One-Hot Encoder | Encodes `sender_role` (`FACULTY`, `ADMIN`, etc.) |
| [`importance_inference_logreg.joblib`] | Inference-safe Importance Classifier | 3 classes (`HIGH`, `LOW`, `MEDIUM`). Trained **without** unavailable gold flags |
| [`importance_inference_tfidf.joblib`] | TF-IDF for Importance Model | Text features for importance rating |
| [`importance_inference_sender_role.joblib`]| Sender One-Hot Encoder | Sender features for importance model |
| [`inference_feature_manifest.json`] | Specification Manifest | Maps model dependencies and training parameters |

### 2.2 Datasets & Preprocessing
* **Raw Dataset:** [`CampusAI_raw_dataset.csv`] (885 KB)
* **Cleaned & Preprocessed:** [`CampusAI_cleaned_dataset.csv`] & [`CampusAI_preprocessed_dataset.csv`]\
* **Full Pipeline Notebook/Script:** [`CampusAI_Preprocessing_Pipeline.py`]
* **Information Extraction Datasets:**
  * [`classroom_change_qa_dataset.jsonl`]
  * [`deadline_qa_dataset.jsonl`]
  * [`ner_dataset.jsonl`]
  * [`action_extraction_dataset.csv`]

### 2.3 Evaluated Baseline Performance
From `NLP PROJECT/campusai_artifacts/model_comparison_table.csv` and evaluation reports:
* **Category Classifier:** Accuracy **98.67%**, Macro F1 **98.70%**, Weighted F1 **98.65%**
* **Importance Classifier:** Accuracy **99.67%**, Macro F1 **99.72%**, Weighted F1 **99.67%** (Inference-safe test accuracy: **99.33%**)

---

## 3. Baseline Verification Test Run

The existing unit tests in [`test_campusai_inference.py`] were executed:
```powershell
python -m unittest discover -s "NLP PROJECT/campusai_artifacts" -p "test_campusai_inference.py" -v
```
**Result:** 12 tests passed in 2.61s (`OK`).

### Sample Inference Output
Calling `process_email(subject="Exam timetable published", body="The examination begins on 22 August 2026. Submit your hall ticket.", sender_role="ADMIN")` produces:
```json
{
  "category": "EXAM",
  "category_confidence": 0.824,
  "importance": "HIGH",
  "importance_confidence": 0.791,
  "uncertain": false,
  "dates": ["22 August 2026"],
  "times": [],
  "has_deadline": false,
  "deadline_date": null,
  "has_classroom_change": false,
  "old_location": null,
  "new_location": null,
  "has_exam": true,
  "has_assignment": false,
  "action_items": ["submit"]
}
```

---

## 4. Gap Analysis & What Must Be Built

| Component | Target Location | Status | Action Required |
|---|---|---|---|
| **NLP Reusable Module** | `CAMPUS AI/nlp` | Pending | Wrap Person 1's models with date normalization, timetable change extraction, and structured schemas. |
| **Backend REST API** | `CAMPUS AI/backend` | Missing | Scaffold FastAPI app, routers (`/auth`, `/emails`, `/events`, `/notion`, `/notes`, `/chat`, `/campus`), Pydantic models. |
| **Database & ORM** | `CAMPUS AI/backend` | Missing | SQLAlchemy models (`User`, `Email`, `Prediction`, `Event`, `NotionSync`, `Floor`, `Room`), Alembic migrations. SQLite support for local dev, PostgreSQL for production. |
| **Android Application** | `CAMPUS AI/android-app` | Missing | Scaffold clean Android Gradle project (Java + XML): Login, Dashboard, Email List, Detail view, Proposal Review dialog, Timetable, Notes, Indoor Map. |
| **Documentation & Evaluation** | `CAMPUS AI/docs` | Scaffolding | API documentation, Architecture diagrams, Evaluation report, User guides. |

---

## 5. Phase 1 Roadmap: NLP Stabilization & Service Packaging

1. **Replicate & Encapsulate NLP Service:** In `CAMPUS AI/nlp/`, create `service.py` that imports and encapsulates inference safely with fallback handling.
2. **Enhanced Entity Extraction:** Add normalized date parsing (ISO format), room number validation, and timetable change proposal generator.
3. **Automated Evaluation Script:** Package a self-contained evaluation runner that tests on `CampusAI_cleaned_dataset.csv` and outputs confusion matrices and classification reports into `CAMPUS AI/docs/`.
