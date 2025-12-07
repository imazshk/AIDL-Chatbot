# Q25. Build a Gemini-powered assistant that uses PDF + TXT + CSV to answer root cause questions.

import streamlit as st
import pandas as pd
import PyPDF2
import google.generativeai as genai

# =====================
# Configure Gemini API (your key inserted directly)
# =====================
genai.configure(api_key="AIzaSyC_DKHOj4zJCmZieBe31KOTIbZ70Aq63Sw")

# ✅ Use the flash model (better quota limits)
model = genai.GenerativeModel("gemini-1.5-flash")

# =====================
# Load Data
# =====================
csv_path = "customer_interaction.csv"
pdf_path = "div_B_escalation_audit.pdf"
txt_path = "div_B_ops_report.txt"

# Load CSV safely
try:
    df = pd.read_csv(csv_path)
except Exception as e:
    df = pd.DataFrame()
    st.error(f"Error loading CSV: {e}")

# Load PDF text
pdf_text = ""
try:
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                pdf_text += content + "\n"
except Exception as e:
    st.error(f"Error loading PDF: {e}")

# Load TXT text
txt_text = ""
try:
    with open(txt_path, "r") as f:
        txt_text = f.read()
except Exception as e:
    st.error(f"Error loading TXT: {e}")

# =====================
# Streamlit UI
# =====================
st.set_page_config(page_title="Root Cause Gemini Assistant", layout="wide")
st.title("🤖 Root Cause Assistant (CSV + PDF + TXT with Gemini)")

st.write("Ask me questions about escalations, unresolved tickets, failures, or process risks.")

# User input
user_query = st.text_area("Enter your question:")

# =====================
# Gemini Response
# =====================
if user_query:
    try:
        # ✅ Limit input size to avoid quota/token issues
        context = f"""
        Use ONLY the following data to answer the question.
        Answer DIRECTLY and CONCISELY.
        If the answer is not found, reply: "Not found in provided files."

        === CSV (Customer Interactions sample) ===
        {df.head(10).to_string() if not df.empty else "No CSV data loaded."}

        === PDF (Escalation Audit extract) ===
        {pdf_text[:1000]}

        === TXT (Ops Report extract) ===
        {txt_text[:1000]}
        """

        prompt = f"{context}\n\nQuestion: {user_query}\nAnswer directly:"

        # Call Gemini
        response = model.generate_content(prompt)

        # Show answer
        st.subheader("Answer")
        st.write(response.text.strip() if hasattr(response, "text") else str(response))

    except Exception as e:
        st.error(f"Error generating response: {e}")
