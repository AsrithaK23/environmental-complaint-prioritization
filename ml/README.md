# NLP / AI Model — Environmental Complaint Classification

## 📌 Overview

The NLP / AI module is responsible for automatically understanding and classifying environmental complaints submitted through the **AI-Based Environmental Complaint Prioritization System**.

The module receives complaint text as input, processes the text using Natural Language Processing (NLP), converts the text into numerical features using **TF-IDF**, and uses a machine-learning classifier to predict the type of environmental complaint.

The module also provides a confidence score for each prediction and exposes a simple prediction interface that can be used by the backend.

---

## 🎯 Purpose

The primary purpose of this module is to answer:

> **"What type of environmental complaint is this?"**

For example:

### Input

```text
Garbage has not been collected near the hostel for three days.
```

### Output

```text
Category: Waste Management
Confidence: 0.93
```

The predicted category can then be passed to the backend for further complaint processing.

---

## 👤 Module Responsibility

This module is developed as part of **Person 2 — NLP / AI Model**.

### Responsibilities

- Preprocess complaint text
- Clean and normalize complaint text
- Convert complaint text into TF-IDF features
- Train the complaint classification model
- Evaluate model performance
- Save the trained classifier
- Save the TF-IDF vectorizer
- Load the trained model for prediction
- Predict complaint category
- Calculate prediction confidence
- Provide a reusable prediction interface for backend integration
- Document the ML pipeline

### Outside the Scope of This Module

The following functionality is handled by other project modules:

- User registration and login
- Authentication and authorization
- MySQL database management
- Complaint submission API
- Complaint priority calculation
- Department assignment/routing
- Complaint status management
- Staff management
- Admin dashboard
- Frontend UI

The NLP module only determines the **complaint category and confidence score**.

---

# 🏗️ ML Pipeline

The complete NLP pipeline is:

```text
                Complaint Text
                      │
                      ▼
             Text Preprocessing
                      │
                      ▼
              Cleaned Complaint
                      │
                      ▼
               TF-IDF Vectorizer
                      │
                      ▼
              Numerical Features
                      │
                      ▼
          Machine Learning Classifier
                      │
                      ▼
              Predicted Category
                      │
                      ▼
             Confidence Score
```

---

# 📂 Directory Structure

The ML module follows this structure:

```text
ml/
│
├── models/
│   ├── complaint_classifier.pkl
│   └── tfidf_vectorizer.pkl
│
├── preprocessing.py
├── train.py
├── predict.py
├── test_model.py
└── README.md
```

---

# 📄 File Description

## `preprocessing.py`

Contains the text preprocessing function.

The preprocessing stage:

- Converts text to lowercase
- Removes URLs
- Removes email addresses
- Removes unnecessary characters
- Removes extra spaces
- Produces normalized complaint text

Main function:

```python
clean_text(text)
```

Example:

```python
from ml.preprocessing import clean_text

text = "Garbage near Hostel B has NOT been collected!!!"

cleaned = clean_text(text)

print(cleaned)
```

---

## `train.py`

Contains the complete model training pipeline.

The training process includes:

1. Loading the cleaned dataset
2. Validating required columns
3. Removing missing values
4. Cleaning complaint text
5. Splitting the dataset into training and testing sets
6. Creating TF-IDF features
7. Training the classifier
8. Generating predictions
9. Evaluating the model
10. Saving the trained classifier
11. Saving the TF-IDF vectorizer

Run the training process using:

```bash
python ml/train.py
```

---

## `predict.py`

Loads the trained model and TF-IDF vectorizer and provides the prediction interface.

Main function:

```python
predict_complaint(text)
```

Example:

```python
from ml.predict import predict_complaint

result = predict_complaint(
    "Garbage has not been collected near the hostel"
)

print(result)
```

Expected output format:

```python
{
    "category": "Waste Management",
    "confidence": 0.93
}
```

The exact confidence value depends on the trained model.

---

## `test_model.py`

Used to test the trained model with multiple sample complaints.

Run:

```bash
python ml/test_model.py
```

This helps verify that the trained model is producing predictions correctly before backend integration.

---

## `models/`

Contains the trained machine-learning artifacts.

### `complaint_classifier.pkl`

Serialized trained classification model.

### `tfidf_vectorizer.pkl`

Serialized TF-IDF vectorizer used to convert complaint text into the same feature representation used during training.

Both files must be generated from the same training process.

---

# 🗂️ Dataset

The NLP model uses the cleaned complaint dataset prepared by the data-preparation module.

Expected dataset location:

```text
dataset/complaints_cleaned.csv
```

Expected columns:

```text
complaint_text
category
```

### Example

| complaint_text | category |
|---|---|
| Garbage has not been collected near the hostel | Waste Management |
| Sewage water is leaking near the cafeteria | Water / Sanitation |
| Smoke is coming from the generator | Air Pollution |
| Loud music is disturbing students | Noise Pollution |

---

# 🏷️ Complaint Categories

The classifier is designed to classify complaints into the following environmental categories:

1. **Waste Management**
2. **Water / Sanitation**
3. **Air Pollution**
4. **Noise Pollution**
5. **Energy-related Issues**
6. **Greenery / Landscaping**
7. **Other**

The final model is trained using the categories available in the cleaned dataset.

---

# 🔤 Text Preprocessing

Before the complaint text is passed to the machine-learning model, it is cleaned using the preprocessing pipeline.

The preprocessing includes:

```text
Raw Complaint
      │
      ▼
Convert to lowercase
      │
      ▼
Remove URLs
      │
      ▼
Remove email addresses
      │
      ▼
Remove unnecessary characters
      │
      ▼
Remove extra spaces
      │
      ▼
Clean Complaint
```

Example:

### Original

```text
"Garbage near Hostel B hasn't been collected for 3 days!!!"
```

### Processed

```text
"garbage near hostel b hasn t been collected for days"
```

The same preprocessing function is used during both **training and prediction** to maintain consistency.

---

# 🔢 TF-IDF Feature Extraction

The module uses **TF-IDF (Term Frequency-Inverse Document Frequency)** to convert complaint text into numerical features.

The vectorizer considers:

- Individual words
- Word combinations / n-grams
- Important terms within the complaint dataset

The configured vectorizer uses:

```python
TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    stop_words="english"
)
```

### Configuration

| Parameter | Value | Purpose |
|---|---:|---|
| `max_features` | 5000 | Limits the number of features |
| `ngram_range` | `(1, 2)` | Uses unigrams and bigrams |
| `stop_words` | `english` | Removes common English stop words |

The vectorizer is fitted only on the training data and is then reused during prediction.

---

# 🤖 Machine Learning Model

The current implementation uses **Logistic Regression** as the text classification model.

Configuration:

```python
LogisticRegression(
    max_iter=2000
)
```

The classifier learns the relationship between:

```text
Complaint Text Features
          ↓
Environmental Category
```

The trained classifier is saved as:

```text
ml/models/complaint_classifier.pkl
```

---

# 🧪 Training and Testing

The dataset is divided into:

```text
Training Dataset
       +
Testing Dataset
```

The current training configuration uses:

```python
test_size=0.20
random_state=42
stratify=y
```

This means:

- 80% of the data is used for training
- 20% is used for testing
- The random state provides reproducibility
- Stratification helps preserve category distribution

---

# 📊 Model Evaluation

The model is evaluated using:

### Accuracy

Measures the overall percentage of correctly classified complaints.

### Precision

Measures how many complaints predicted as a category actually belong to that category.

### Recall

Measures how many complaints belonging to a category were correctly identified.

### F1-Score

Provides a combined measure of precision and recall.

### Confusion Matrix

Shows the relationship between actual and predicted categories and helps identify categories that the model confuses with one another.

The training script prints:

```text
Accuracy
Classification Report
Confusion Matrix
```

---

# 📈 Model Results

Final model results should be added here after training with the final dataset.

Example format:

```text
Accuracy  : [ADD FINAL RESULT]
Precision : [ADD FINAL RESULT]
Recall    : [ADD FINAL RESULT]
F1-Score  : [ADD FINAL RESULT]
```

> Do not enter estimated or sample values here. Replace these placeholders with the actual results obtained after training the final dataset.

---

# 💾 Model Artifacts

After successful training, the following files are generated:

```text
ml/models/
│
├── complaint_classifier.pkl
└── tfidf_vectorizer.pkl
```

These files are required for prediction.

The classifier and vectorizer should always correspond to the same training run.

---

# ▶️ Installation

From the project root, install the required Python packages:

```bash
pip install pandas numpy scikit-learn joblib
```

Alternatively:

```bash
pip install -r requirements.txt
```

---

# 🚀 Training the Model

Make sure the dataset is available at:

```text
dataset/complaints_cleaned.csv
```

Then run:

```bash
python ml/train.py
```

The training script will:

```text
Load Dataset
     ↓
Validate Dataset
     ↓
Clean Text
     ↓
Split Data
     ↓
Create TF-IDF Features
     ↓
Train Classifier
     ↓
Evaluate Model
     ↓
Save Model
```

After successful training:

```text
ml/models/complaint_classifier.pkl
ml/models/tfidf_vectorizer.pkl
```

should be available.

---

# 🔍 Making Predictions

Once the model has been trained, predictions can be generated using:

```python
from ml.predict import predict_complaint

result = predict_complaint(
    "Garbage has not been collected near the hostel"
)

print(result)
```

Example output:

```python
{
    "category": "Waste Management",
    "confidence": 0.93
}
```

---

# 🧩 Prediction Interface

The main interface provided to the backend is:

```python
predict_complaint(complaint_text)
```

### Input

```python
complaint_text: str
```

Example:

```python
"Water is leaking from a pipe near the cafeteria."
```

### Output

```python
{
    "category": "Water / Sanitation",
    "confidence": 0.91
}
```

### Output fields

| Field | Type | Description |
|---|---|---|
| `category` | `str` | Predicted environmental complaint category |
| `confidence` | `float` | Model prediction confidence |

---

# 🔗 Backend Integration

The backend can use the NLP model through the prediction function.

Example:

```python
from ml.predict import predict_complaint

result = predict_complaint(complaint_text)

category = result["category"]
confidence = result["confidence"]
```

The backend can then continue with the remaining complaint-processing workflow.

For example:

```text
Complaint Submitted
        ↓
NLP Classification
        ↓
Category + Confidence
        ↓
Priority Engine
        ↓
Department Routing
        ↓
Database
```

The NLP module does **not** perform priority calculation or department assignment.

---

# 🧪 Example Predictions

### Example 1 — Waste Management

Input:

```text
Garbage has not been collected near the hostel for three days.
```

Expected category:

```text
Waste Management
```

---

### Example 2 — Water / Sanitation

Input:

```text
There is sewage water leaking near the cafeteria.
```

Expected category:

```text
Water / Sanitation
```

---

### Example 3 — Air Pollution

Input:

```text
The generator is producing a lot of smoke near the academic block.
```

Expected category:

```text
Air Pollution
```

---

### Example 4 — Noise Pollution

Input:

```text
Very loud music is disturbing students in the hostel.
```

Expected category:

```text
Noise Pollution
```

---

### Example 5 — Energy-related Issues

Input:

```text
Lights in the corridor remain switched on throughout the day.
```

Expected category:

```text
Energy-related Issues
```

---

### Example 6 — Greenery / Landscaping

Input:

```text
The plants around the academic block are not being maintained.
```

Expected category:

```text
Greenery / Landscaping
```

> These examples are for testing the prediction interface. Actual predictions depend on the trained model and dataset.

---

# 🛠️ Testing Checklist

Before handing the module to the backend team, verify:

```text
☐ Dataset loads correctly
☐ Required dataset columns exist
☐ Text preprocessing works
☐ TF-IDF vectorizer trains successfully
☐ Classifier trains successfully
☐ Accuracy is calculated
☐ Precision/Recall/F1 are calculated
☐ Confusion matrix is generated
☐ Model is saved
☐ Vectorizer is saved
☐ Model loads successfully
☐ Prediction function works
☐ Confidence score is returned
☐ Multiple complaint examples are tested
☐ Backend prediction interface is documented
```

---

# ⚠️ Important Notes

### 1. Use the same preprocessing during training and prediction

The complaint text must be processed using:

```python
clean_text()
```

both during training and prediction.

### 2. Do not fit the vectorizer again during prediction

During prediction, use:

```python
vectorizer.transform(...)
```

and not:

```python
vectorizer.fit_transform(...)
```

The vectorizer must use the vocabulary learned during training.

### 3. Keep the model and vectorizer together

These two files belong to the same trained pipeline:

```text
complaint_classifier.pkl
tfidf_vectorizer.pkl
```

### 4. Retrain when the training dataset changes significantly

If the final cleaned dataset is changed substantially, the model should be retrained.

---

# 👥 Module Handoff

The NLP module provides the following to the backend team:

```text
┌────────────────────────────────────┐
│        NLP / AI MODULE             │
├────────────────────────────────────┤
│                                    │
│ preprocessing.py                   │
│ train.py                           │
│ predict.py                         │
│ complaint_classifier.pkl           │
│ tfidf_vectorizer.pkl               │
│                                    │
└────────────────┬───────────────────┘
                 │
                 │ predict_complaint()
                 ▼
┌────────────────────────────────────┐
│          BACKEND MODULE            │
│                                    │
│ Category + Confidence              │
│        ↓                           │
│ Priority Engine                    │
│        ↓                           │
│ Department Routing                 │
│        ↓                           │
│ Database                           │
│                                    │
└────────────────────────────────────┘
```

---

# 👨‍💻 Person 2 Deliverables

The completed NLP / AI module consists of:

```text
1. preprocessing.py
2. train.py
3. predict.py
4. test_model.py
5. complaint_classifier.pkl
6. tfidf_vectorizer.pkl
7. Model evaluation results
8. Prediction interface
9. ML documentation
```

---

# 📌 Current Status

| Component | Status |
|---|---|
| Text preprocessing | In development / Ready |
| TF-IDF pipeline | Ready |
| Classifier pipeline | Ready |
| Model training | Pending final dataset |
| Model evaluation | Pending final training |
| Trained classifier | Generated after final training |
| TF-IDF vectorizer | Generated after final training |
| Prediction interface | Ready |
| Local testing | To be completed |
| Backend integration | Handoff to backend team |

---

## 🔑 Summary

The NLP module converts an unstructured environmental complaint into a structured classification result:

```text
User Complaint
      ↓
Text Preprocessing
      ↓
TF-IDF
      ↓
Machine Learning Classifier
      ↓
Environmental Category
      ↓
Confidence Score
      ↓
Backend
```

The module's primary responsibility is **complaint category classification**. Priority calculation, department routing, database management, complaint status, and user interfaces are handled by the corresponding modules of the overall system.