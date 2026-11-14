# 🛠️ OpsAssist: AI Field Operations & IT Support Agent

**OpsAssist** is an enterprise-ready AI triage agent built to assist field technicians and IT support teams with rapid hardware diagnostics and automated incident escalation.

## 🚀 Key Features
* **SOP-Grounded Troubleshooting:** Uses retrieval-augmented prompting to answer hardware, network, and power issues strictly from verified Standard Operating Procedures (SOPs), preventing hallucinations.
* **Autonomous Agentic Escalation:** Detects out-of-scope incidents and automatically writes structured support tickets into a backend SQL database.
* **Live Operational Queue:** Provides real-time visibility into escalated incidents directly from the operator dashboard.

## 🏗️ Tech Stack
* **Language:** Python 3.10+
* **LLM & SDK:** Google Gemini (`gemini-2.5-flash`) via `google-genai`
* **Frontend UI:** Streamlit
* **Database:** SQLite3

## 💻 Local Setup & Testing
1. Clone the repository:
   ```bash
   git clone https://github.com
   cd ops-assist-agent
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```
