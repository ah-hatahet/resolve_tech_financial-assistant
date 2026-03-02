# Financial Assistant — Real Estate Company

A full-stack AI-powered financial assistant web application built for a real estate investment company. The platform combines structured database queries, SEC EDGAR financial data, classic machine learning models deployed on AWS SageMaker, and a generative AI chatbot powered by Google Vertex AI ADK.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web Interface                   │
│  Filters │ Financial Summary │ SEC Data │ ML Predictions    │
│                    AI Chatbot Panel                         │
└────────────┬──────────────┬──────────────┬──────────────────┘
             │              │              │
             ▼              ▼              ▼
     ┌──────────────┐ ┌──────────┐ ┌─────────────────────┐
     │  PostgreSQL  │ │   SEC    │ │   AWS SageMaker      │
     │  Database    │ │  EDGAR   │ │  ┌─────────────────┐ │
     │  properties  │ │  XBRL    │ │  │ Regression      │ │
     │  financials  │ │   API    │ │  │ Classification  │ │
     └──────────────┘ └──────────┘ │  └─────────────────┘ │
             │                     └─────────────────────────┘
             │
             ▼
     ┌──────────────────────────────────────────┐
     │         Google Vertex AI ADK             │
     │   Agent: financial_assistant             │
     │   Model: gemini-2.0-flash                │
     │   Tools:                                 │
     │   - query_financials                     │
     │   - query_properties                     │
     │   - query_press_releases                 │
     │   - query_sec_filings                    │
     └──────────────────────────────────────────┘
             │
             ▼
     ┌──────────────────────────────────────────┐
     │         AWS Bedrock                      │
     │   Model: amazon.nova-pro-v1:0            │
     │   Use: Portfolio summarization           │
     └──────────────────────────────────────────┘
```

---

## Project Structure

```
financial-assistant/
├── app/
│   ├── app.py                  # Streamlit web interface
│   ├── chatbot.py              # Vertex AI ADK agent setup
│   ├── tools.py                # Chatbot tool definitions
│   └── sec_edgar.py            # SEC EDGAR XBRL API client
├── database/
│   └── db_connection.py        # PostgreSQL connection and queries
├── models/
│   ├── train_regression.py         # Train Random Forest Regressor
│   ├── train_classification.py     # Train Logistic Regression classifier
│   ├── inference_regression.py     # SageMaker inference script (regression)
│   ├── inference_classification.py # SageMaker inference script (classification)
│   ├── predict_regression.py       # Local prediction utility
│   ├── predict_classification.py   # Local prediction utility
│   ├── deploy_to_sagemaker.py      # SageMaker deployment script
│   ├── random_forest_regressor.pkl # Trained regression model artifact
│   └── logistic_regression_model.pkl # Trained classification model artifact
├── data/
│   ├── bank-full.csv           # UCI Bank Marketing dataset
│   └── press_releases.json     # Company press releases
├── create_tables.sql           # PostgreSQL schema definition
├── seed_data.sql               # Sample data for database
├── requirements.txt            # Python dependencies
├── test_db.py                  # Database connection test
└── financial-assistant-ah-6a888c6ca467.json  # GCP service account key
```

---

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- AWS account with SageMaker and Bedrock access
- GCP project with Vertex AI API enabled
- AWS CLI configured (`aws configure`)

---

## Local Setup

### 1. Clone the repository and create a virtual environment

```bash
git clone <repo-url>
cd financial-assistant
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up the PostgreSQL database

Make sure PostgreSQL is running locally, then create the database:

```bash
psql -U <your_user> -c "CREATE DATABASE real_estate_db;"
```

Run the SQL scripts to create tables and populate sample data:

```bash
psql -U <your_user> -d real_estate_db -f create_tables.sql
psql -U <your_user> -d real_estate_db -f seed_data.sql
```

Update `database/db_connection.py` with your PostgreSQL credentials:

```python
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "real_estate_db"
```

### 4. Configure GCP credentials

Place your GCP service account JSON key file in the project root and update the path in `app/chatbot.py`:

```python
SA_KEY_PATH = os.path.join(os.path.dirname(__file__), '..', 'your-key-file.json')
GCP_PROJECT_ID = "your-gcp-project-id"
```

### 5. Configure AWS credentials

```bash
aws configure
```

Enter your AWS Access Key ID, Secret Access Key, and set the default region to `us-east-1`.

### 6. Run the application

```bash
streamlit run app/app.py
```

---

## Cloud Setup

### AWS SageMaker — Model Deployment

Both ML models are deployed as SageMaker hosted endpoints. To deploy or redeploy them:

```bash
cd models
python deploy_to_sagemaker.py
```

This script will:
- Package each trained model with its inference script into a `.tar.gz` artifact
- Upload the artifacts to S3 (`s3://financial-assistant-ah/models/`)
- Create and deploy two SageMaker endpoints:
  - `housing-regression-endpoint` — California Housing price prediction
  - `bank-classification-endpoint` — Bank subscription classification

Deployment takes approximately 10–15 minutes per endpoint. The script waits for both to reach `InService` status before exiting.

### GCP Vertex AI — Chatbot Agent

The chatbot uses the Google Agent Development Kit (ADK) with Gemini 2.0 Flash. No manual deployment is required — the agent is instantiated at runtime in `app/chatbot.py` using the GCP service account credentials.

Make sure the following APIs are enabled in your GCP project:
- Vertex AI API
- Generative Language API

### AWS Bedrock — Portfolio Summarization

No deployment is required. The app calls the `amazon.nova-pro-v1:0` model directly via the Bedrock runtime API. Ensure your IAM user has the `AmazonBedrockFullAccess` policy attached.

---

## Machine Learning Models

### Regression — California Housing Price Prediction

**Dataset:** California Housing (scikit-learn built-in)
**Model:** Random Forest Regressor (100 estimators)
**Features:** MedInc, HouseAge, AveRooms, AveBedrms, Population, AveOccup, Latitude, Longitude
**Target:** Median house value (×$100,000)

To retrain:
```bash
cd models
python train_regression.py
```

Evaluation metrics are printed on completion (RMSE, MAE, R² Score). The trained model is saved as `random_forest_regressor.pkl`.

### Classification — Bank Subscription Prediction

**Dataset:** UCI Bank Marketing (`data/bank-full.csv`)
**Model:** Logistic Regression with preprocessing pipeline
**Features:** Age, job, marital status, education, balance, contact type, campaign data, and more
**Target:** Binary — will the customer subscribe? (1 = yes, 0 = no)

The model uses a scikit-learn Pipeline with:
- `StandardScaler` for numeric features
- `OneHotEncoder` for categorical features
- `LogisticRegression` (max_iter=1000)

To retrain:
```bash
cd models
python train_classification.py
```

Evaluation metrics printed on completion (Accuracy, Precision, Recall, F1, Confusion Matrix). The trained model is saved as `logistic_regression_model.pkl`.

---

## Chatbot Query Routing

The chatbot is built with the Google ADK `Agent` class and uses Gemini 2.0 Flash as the underlying model. It is equipped with four tools and routes queries automatically based on the question content:

| Tool | Triggered by |
|---|---|
| `query_financials` | Questions about revenue, net income, expenses, or financial performance |
| `query_properties` | Questions about specific properties, metro areas, square footage, or property types |
| `query_press_releases` | Questions about company news, acquisitions, expansions, or announcements |
| `query_sec_filings` | Questions about SEC filings, 10-K/10-Q reports, or officially reported earnings |

The agent can call multiple tools in a single response if the question spans more than one data source. For example, asking about Chicago industrial properties with revenue details will trigger both `query_properties` and `query_financials`.

Example queries:
- "What was the total net income across all properties?"
- "Show me industrial properties in the Chicago region"
- "Did the company announce any acquisitions recently?"
- "What revenue did Prologis report in their last 10-K?"

---

## Multi-Cloud Architecture

| Service | Cloud | Purpose |
|---|---|---|
| Vertex AI ADK (Gemini 2.0 Flash) | GCP | Natural language chatbot |
| SageMaker Endpoints | AWS | ML model hosting and inference |
| Bedrock (Amazon Nova Pro) | AWS | Portfolio summarization |
| PostgreSQL | Local | Property and financial data storage |
| SEC EDGAR API | Public | Real-world financial filings |

---

## Dependencies

```
google-adk
google-cloud-aiplatform
streamlit
sqlalchemy
psycopg2-binary
pandas
joblib
boto3
scikit-learn
numpy
requests
```

Install all with:
```bash
pip install -r requirements.txt
```
