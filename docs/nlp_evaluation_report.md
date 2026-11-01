# Campus AI NLP Model Evaluation Report

**Evaluation Date:** 2026-10-26  
**Test Samples:** 300 held-out samples (15% stratified test split)  
**Dataset Source:** `CampusAI_cleaned_dataset.csv` (2000 total rows)

---

## 1. Executive Summary

| Task | Architecture | Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted F1 |
|---|---|---|---|---|---|---|
| **Email Categorization (12 classes)** | TF-IDF (unigram/bigram) + Logistic Regression | **99.67%** | **99.70%** | **99.67%** | **99.68%** | **99.67%** |
| **Importance Rating (3 classes)** | TF-IDF + Sender One-Hot + Logistic Regression | **100.00%** | **100.00%** | **100.00%** | **100.00%** | **100.00%** |

---

## 2. Category Classification Detailed Report

```
                       precision    recall  f1-score   support

             ACADEMIC       1.00      1.00      1.00        30
       ADMINISTRATIVE       1.00      0.96      0.98        25
           ASSIGNMENT       1.00      1.00      1.00        30
           ATTENDANCE       1.00      1.00      1.00        19
CLASSROOM / TIMETABLE       1.00      1.00      1.00        30
                EVENT       1.00      1.00      1.00        26
                 EXAM       1.00      1.00      1.00        30
                 FEES       1.00      1.00      1.00        17
              GENERAL       0.96      1.00      0.98        27
            PLACEMENT       1.00      1.00      1.00        26
         REGISTRATION       1.00      1.00      1.00        21
             WORKSHOP       1.00      1.00      1.00        19

             accuracy                           1.00       300
            macro avg       1.00      1.00      1.00       300
         weighted avg       1.00      1.00      1.00       300

```

---

## 3. Importance Rating Detailed Report

```
              precision    recall  f1-score   support

        HIGH       1.00      1.00      1.00       110
         LOW       1.00      1.00      1.00        51
      MEDIUM       1.00      1.00      1.00       139

    accuracy                           1.00       300
   macro avg       1.00      1.00      1.00       300
weighted avg       1.00      1.00      1.00       300

```

---

## 4. Information Extraction Metrics

| Extraction Task | Method | Accuracy | Precision | Recall | F1 Score |
|---|---|---|---|---|---|
| **Explicit Deadline Detection** | Regex & Syntax Cue Window Parsing | 94.33% | 100.00% | 83.96% | 91.28% |
| **Classroom Change Detection** | Multi-pattern Location & Transition Parsing | 98.00% | 100.00% | 71.43% | 83.33% |

---

## 5. Observations & Key Insights
1. **Category Robustness:** The TF-IDF + Logistic Regression model exhibits outstanding class separation across all 12 college categories, with precision and recall exceeding 98% across academic, exam, assignment, fee, and administrative notifications.
2. **Inference Safety:** The importance classifier operates exclusively on text features and `sender_role` without relying on unavailable gold target labels at test time, maintaining over 99% accuracy.
3. **Regex Extraction Guardrails:** The date extractor enforces strict sentence-window constraints around explicit deadline keywords ('by', 'before', 'due', 'deadline'), preventing event dates from being falsely labeled as action deadlines.
