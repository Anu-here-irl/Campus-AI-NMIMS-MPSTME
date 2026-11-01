# Natural Language Processing & Machine Learning — Semester V Academic Notes
Author: Dept of Computer Engineering & IT
Course Code: CS-504

## Chapter 1: Text Representation & Preprocessing
NLP pipelines convert unstructured textual documents into numerical feature representations suitable for machine learning algorithms.

### Preprocessing Steps
1. **Tokenization:** Segmenting running text into individual words, tokens, or subwords.
2. **Case Folding & Lowercasing:** Standardizing character casing to reduce vocabulary size.
3. **Stopword Removal:** Eliminating high-frequency grammatical function words (e.g., 'the', 'is', 'at') that convey minimal topic distinction.
4. **Stemming & Lemmatization:**
   - *Stemming (Porter/Snowball):* Heuristic rule-based stripping of word affixes to produce a stem (e.g., 'studying' -> 'studi').
   - *Lemmatization (WordNet):* Morphological analysis using a vocabulary and part-of-speech tag to return the base dictionary lemma (e.g., 'better' -> 'good').

### Feature Extraction Models
- **Bag-of-Words (BoW):** Counts token frequencies across documents. Ignores grammatical order and syntax.
- **TF-IDF (Term Frequency - Inverse Document Frequency):** Weights words by their relative importance.
  - Term Frequency: TF(t, d) = (Number of times t appears in document d) / (Total words in d).
  - Inverse Document Frequency: IDF(t, D) = log(Total documents N / Documents containing t).
  - High TF-IDF weight indicates a word is frequent in the specific document but rare across the entire corpus, marking it as a strong discriminative feature.

## Chapter 2: Classification Models & Evaluation Metrics
### Logistic Regression for Text Classification
Logistic Regression is a linear discriminative model applying the sigmoid / softmax function over a weighted sum of input features:
P(Y=1|X) = 1 / (1 + exp(- (w^T * x + b))).
- Highly effective, fast, and interpretable for high-dimensional sparse TF-IDF text features.
- Uses L1 (Lasso) or L2 (Ridge) regularization to prevent overfitting on noisy vocabularies.

### Evaluation Metrics
- **Accuracy:** Total correct predictions / Total instances. Can be misleading under class imbalance.
- **Precision:** True Positives / (True Positives + False Positives). Measures exactness of positive predictions.
- **Recall (Sensitivity):** True Positives / (True Positives + False Negatives). Measures completeness of detecting actual positives.
- **F1-Score:** Harmonic mean of Precision and Recall: 2 * (Precision * Recall) / (Precision + Recall).
- **Confusion Matrix:** 2x2 or N-class grid tabulating True Positives, False Positives, True Negatives, and False Negatives.

## Chapter 3: Semantic Embeddings & Modern RAG
- **Word2Vec & Dense Embeddings:** Continuous vector spaces mapping semantic meaning such that vectors for synonyms are close in Euclidean and cosine space (e.g., Skip-Gram and CBOW architectures).
- **Retrieval-Augmented Generation (RAG):** Combines information retrieval with generative language models. Instead of relying solely on parametric weights, RAG retrieves relevant document chunks from an external knowledge base (like course notes) and provides them as grounding context to the generation model, preventing hallucinations and enabling verifiable source citations.
