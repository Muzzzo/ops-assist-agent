import streamlit as st
import sqlite3
import os
import time
from datetime import datetime
from google import genai
from google.genai import types

# Initialize SQLite database for automated ticket logging
conn = sqlite3.connect("tickets.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tickets 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, issue TEXT, status TEXT, created_at TEXT)''')
conn.commit()

# Load SOP Knowledge Base
with open("knowledge_base.txt", "r") as f:
    sop_context = f.read()

st.set_page_config(page_title="OpsAssist AI Agent", page_icon="🛠️", layout="wide")
st.title("🛠️ OpsAssist: Field & IT Support Agent")
st.caption("AI-powered troubleshooting grounded in company SOPs with automated SQL ticket escalation.")

# Read API key from Streamlit Cloud Secrets, environment variables, or sidebar
api_key = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"].strip()
except Exception:
    pass

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password").strip()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

def generate_with_fallback(client, conversation, system_instruction):
    """Attempts primary model with retry, falling back to secondary model on 503 spikes."""
    models_to_try = ["gemini-3.8-flash", "gemini-3.8-flash-lite"]
    last_error = None

    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=conversation,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2,
                    )
                )
                return response.text
            except Exception as e:
                last_error = e
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    time.sleep(2)
                    continue
                raise e
    raise last_error

if prompt := st.chat_input("Describe the hardware, power, or network issue..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.warning("Please enter your Gemini API key in the sidebar or Streamlit Secrets.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            system_instruction = f"""
            You are an enterprise IT & Field Operations AI Agent. 
            Answer the user's issue strictly using the Standard Operating Procedures (SOPs) provided below.
            Keep your steps clear, concise, and actionable for field technicians.
            If the issue is NOT covered in the SOPs, tell the user you are escalating it to Tier-2 Engineering and add the exact tag [ESCALATE] at the end of your reply.
            
            SOPs:
            {sop_context}
            """

            conversation = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
            
            with st.spinner("Analyzing SOPs & diagnosing..."):
                reply = generate_with_fallback(client, conversation, system_instruction)

            # Agentic Action: Automatically log escalated issues to SQL database
            if "[ESCALATE]" in reply:
                clean_reply = reply.replace("[ESCALATE]", "").strip()
                c.execute("INSERT INTO tickets (issue, status, created_at) VALUES (?, ?, ?)",
                          (prompt, "Escalated to Tier-2", datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                clean_reply += "\n\n✅ **Automated Action:** Ticket logged to SQL database for Tier-2 review."
            else:
                clean_reply = reply

            st.session_state.messages.append({"role": "assistant", "content": clean_reply})
            with st.chat_message("assistant"):
                st.markdown(clean_reply)

        except Exception as e:
            st.error(f"Service temporarily busy ({e}). Please try sending your message again in a few seconds.")

# Sidebar view of live SQL database
with st.sidebar:
    st.divider()
    st.subheader("📋 Live Escalation Queue (SQL)")
    tickets = c.execute("SELECT id, issue, status, created_at FROM tickets ORDER BY id DESC").fetchall()
    if not tickets:
        st.caption("No escalated tickets yet.")
    for t in tickets:
        st.info(f"**Ticket #{t}**\n\n**Issue:** {t}\n\n**Status:** `{t}` ({t})")
