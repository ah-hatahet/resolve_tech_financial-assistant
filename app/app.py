import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from database.db_connection import get_properties, get_financials
from sec_edgar import get_sec_financials
import pandas as pd
from chatbot import handle_query
import boto3
import json

st.set_page_config(page_title="Financial Assistant", layout="wide")

st.title("🏢 Financial Assistant - Real Estate Company")

# AWS credentials from Streamlit secrets
aws_access_key = st.secrets["aws"]["access_key_id"]
aws_secret_key = st.secrets["aws"]["secret_access_key"]
aws_region = st.secrets["aws"]["region"]

# Load Data
properties = get_properties()
financials = get_financials()
combined = pd.merge(properties, financials, on="property_id")

# Sidebar Filters
st.sidebar.header("🔎 Filters")

metro_options = combined["metro_area"].unique()
selected_metro = st.sidebar.selectbox("Select Metro Area", ["All"] + list(metro_options))

property_types = combined["property_type"].unique()
selected_type = st.sidebar.selectbox("Select Property Type", ["All"] + list(property_types))

# Apply Filters
filtered = combined.copy()

if selected_metro != "All":
    filtered = filtered[filtered["metro_area"] == selected_metro]

if selected_type != "All":
    filtered = filtered[filtered["property_type"] == selected_type]

st.header("📊 Filtered Properties")
st.dataframe(filtered)




# Financial Summary
st.header("💰 Financial Summary")

total_revenue = filtered["revenue"].sum()
total_net_income = filtered["net_income"].sum()
total_expenses = filtered["expenses"].sum()

col1, col2, col3 = st.columns(3)

col1.metric("Total Revenue", f"${total_revenue:,.0f}")
col2.metric("Total Net Income", f"${total_net_income:,.0f}")
col3.metric("Total Expenses", f"${total_expenses:,.0f}")





# ----------------------------------
# 🤖 AWS Bedrock — Portfolio Summary
# ----------------------------------

st.subheader("🤖 AI Portfolio Summary")

if st.button("Summarize Portfolio"):
    with st.spinner("Generating summary..."):
        try:
            bedrock = boto3.client("bedrock-runtime", region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key)

            metro_breakdown = filtered.groupby("metro_area")["revenue"].sum().to_dict()
            type_breakdown = filtered.groupby("property_type")["revenue"].sum().to_dict()

            prompt = f"""You are a financial analyst assistant for a real estate company.
Summarize the following portfolio data in 3-4 clear, professional sentences:

- Total Properties: {len(filtered)}
- Total Revenue: ${total_revenue:,.0f} USD
- Total Expenses: ${total_expenses:,.0f} USD
- Total Net Income: ${total_net_income:,.0f} USD
- Revenue by Metro Area: {metro_breakdown}
- Revenue by Property Type: {type_breakdown}

Provide key insights about performance and portfolio composition."""

            response = bedrock.invoke_model(
                modelId="amazon.nova-pro-v1:0",
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {"maxTokens": 300}
                }),
                contentType="application/json",
                accept="application/json"
            )

            result = json.loads(response["body"].read())
            summary = result["output"]["message"]["content"][0]["text"]
            st.success(summary.replace("$", "\\$"))

        except Exception as e:
            st.error(f"Bedrock error: {e}")




# ----------------------------------
# 📈 SEC EDGAR Financials (Prologis)
# ----------------------------------

st.header("📈 SEC EDGAR Financials — Prologis, Inc.")

filing_type = st.radio("Filing Type", ["10-K (Annual)", "10-Q (Quarterly)"], horizontal=True)
form = "10-K" if "10-K" in filing_type else "10-Q"

if st.button("Load SEC Filings"):
    with st.spinner("Fetching data from SEC EDGAR..."):
        try:
            sec_data = get_sec_financials(form=form)

            st.subheader(f"Recent {form} Filings — {sec_data['company']}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Revenue (USD)**")
                if sec_data["revenue"]:
                    df_rev = pd.DataFrame(sec_data["revenue"])
                    df_rev["val"] = df_rev["val"].apply(lambda x: f"${x:,.0f}")
                    df_rev.columns = ["Period End", "Revenue", "Accession", "Form"]
                    st.dataframe(df_rev[["Period End", "Revenue"]], hide_index=True)
                else:
                    st.write("No data found.")

            with col2:
                st.markdown("**Net Income (USD)**")
                if sec_data["net_income"]:
                    df_ni = pd.DataFrame(sec_data["net_income"])
                    df_ni["val"] = df_ni["val"].apply(lambda x: f"${x:,.0f}")
                    df_ni.columns = ["Period End", "Net Income", "Accession", "Form"]
                    st.dataframe(df_ni[["Period End", "Net Income"]], hide_index=True)
                else:
                    st.write("No data found.")

            with col3:
                st.markdown("**Operating Expenses (USD)**")
                if sec_data["operating_expenses"]:
                    df_exp = pd.DataFrame(sec_data["operating_expenses"])
                    df_exp["val"] = df_exp["val"].apply(lambda x: f"${x:,.0f}")
                    df_exp.columns = ["Period End", "Op. Expenses", "Accession", "Form"]
                    st.dataframe(df_exp[["Period End", "Op. Expenses"]], hide_index=True)
                else:
                    st.write("No data found.")

        except Exception as e:
            st.error(f"Failed to fetch SEC data: {e}")




# ----------------------------------
# 📰 Company Press Releases
# ----------------------------------

st.header("📰 Company Press Releases")

import json as _json

press_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'press_releases.json')
with open(press_path, "r") as f:
    press_releases = _json.load(f)

search_term = st.text_input("🔍 Filter by keyword", placeholder="e.g. acquisition, earnings, expansion")

filtered_releases = press_releases
if search_term:
    keyword = search_term.lower()
    filtered_releases = [
        r for r in press_releases
        if keyword in r["title"].lower() or keyword in r["summary"].lower()
    ]

if filtered_releases:
    for release in filtered_releases:
        with st.expander(f"📄 {release['title']} — {release['date']}"):
            st.write(release["summary"])
else:
    st.info("No press releases found matching your search.")




# -------------------------------
# 🏠 Housing Price Prediction
# -------------------------------


st.header("🏠 Predict California Housing Price")


REGRESSION_ENDPOINT = "housing-regression-endpoint"

st.subheader("Enter Housing Features")

col1, col2, col3, col4 = st.columns(4)

with col1:
    MedInc = st.number_input("Median Income", value=5.0)
    HouseAge = st.number_input("House Age", value=20)

with col2:
    AveRooms = st.number_input("Average Rooms", value=5.0)
    AveBedrms = st.number_input("Average Bedrooms", value=1.0)

with col3:
    Population = st.number_input("Population", value=1000)
    AveOccup = st.number_input("Average Occupancy", value=3.0)

with col4:
    Latitude = st.number_input("Latitude", value=34.0)
    Longitude = st.number_input("Longitude", value=-118.0)

if st.button("Predict House Value"):
    features = [
        MedInc, HouseAge, AveRooms, AveBedrms,
        Population, AveOccup, Latitude, Longitude
    ]

    payload = json.dumps({"features": features})

    try:
        runtime = boto3.client("sagemaker-runtime", region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key)
        response = runtime.invoke_endpoint(
            EndpointName=REGRESSION_ENDPOINT,
            ContentType="application/json",
            Body=payload
        )
        result = json.loads(response["Body"].read().decode())
        prediction = result["predicted_value"]
        st.success(f"Predicted Median House Value: ${prediction * 100000:,.0f}")
    except Exception as e:
        st.error(f"SageMaker error: {e}")






# ----------------------------------
# 🏦 Bank Subscription Prediction
# ----------------------------------


st.header("🏦 Predict Bank Subscription (Classification)")

CLASSIFICATION_ENDPOINT = "bank-classification-endpoint"

st.subheader("Enter Customer Information")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", value=35)
    job = st.selectbox("Job", 
        ["management", "technician", "entrepreneur", "blue-collar",
         "retired", "admin.", "services", "self-employed",
         "unemployed", "housemaid", "student", "unknown"])
    marital = st.selectbox("Marital Status", ["married", "single", "divorced"])
    education = st.selectbox("Education", ["primary", "secondary", "tertiary", "unknown"])

with col2:
    default = st.selectbox("Default", ["yes", "no"])
    balance = st.number_input("Balance", value=1500)
    housing = st.selectbox("Housing Loan", ["yes", "no"])
    loan = st.selectbox("Personal Loan", ["yes", "no"])

with col3:
    contact = st.selectbox("Contact Type", ["cellular", "telephone", "unknown"])
    day = st.number_input("Day", value=15)
    month = st.selectbox("Month", 
        ["jan","feb","mar","apr","may","jun",
         "jul","aug","sep","oct","nov","dec"])
    duration = st.number_input("Call Duration", value=200)
    campaign = st.number_input("Campaign", value=1)
    pdays = st.number_input("Previous Days", value=-1)
    previous = st.number_input("Previous Contacts", value=0)
    poutcome = st.selectbox("Previous Outcome", ["unknown", "other", "failure", "success"])

if st.button("Predict Subscription"):
    input_data = {
        "age": age,
        "job": job,
        "marital": marital,
        "education": education,
        "default": default,
        "balance": balance,
        "housing": housing,
        "loan": loan,
        "contact": contact,
        "day": day,
        "month": month,
        "duration": duration,
        "campaign": campaign,
        "pdays": pdays,
        "previous": previous,
        "poutcome": poutcome
    }

    payload = json.dumps(input_data)

    try:
        runtime = boto3.client("sagemaker-runtime", region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key)
        response = runtime.invoke_endpoint(
            EndpointName=CLASSIFICATION_ENDPOINT,
            ContentType="application/json",
            Body=payload
        )
        result = json.loads(response["Body"].read().decode())
        prediction = result["prediction"]
        probability = result["probability"]

        if prediction == 1:
            st.success(f"Customer WILL Subscribe ✅ (Probability: {probability:.2f})")
        else:
            st.error(f"Customer Will NOT Subscribe ❌ (Probability: {probability:.2f})")
    except Exception as e:
        st.error(f"SageMaker error: {e}")




# ----------------------------------
# 💬 AI Chatbot — Powered by Vertex AI ADK
# ----------------------------------

st.header("💬 Financial Assistant Chatbot (Vertex AI ADK)")

# Keep conversation history across reruns
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

# Display previous messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box (pinned to bottom of page)
user_input = st.chat_input("Ask about financials, properties, or press releases...")

if user_input:
    # Show user message immediately
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call the ADK agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = handle_query(user_input, session_id=st.session_state.session_id)
        st.markdown(response)

    st.session_state.chat_history.append({"role": "assistant", "content": response})