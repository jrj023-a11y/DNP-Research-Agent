import os
import time
import datetime
from Bio import Entrez
from google import genai
from google.genai import types
from email.message import EmailMessage
import smtplib

# --- CONFIGURATION ---
Entrez.email = "jrj023@gmail.com"
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
MY_EMAIL = os.environ.get("MAIL_USERNAME")
EMAIL_PASS = os.environ.get("MAIL_PASSWORD")

def fetch_pubmed_valves():
    """Directly queries PubMed for the last 7 days of valve research."""
    today = datetime.date.today()
    past_week = today - datetime.timedelta(days=7)
    date_range = f"{past_week.strftime('%Y/%m/%d')}:{today.strftime('%Y/%m/%d')}"
    
    # Precise query for your clinical focus
    search_query = (f"(TAVR[Title/Abstract] OR SAVR[Title/Abstract] OR 'Mitral Valve'[Title/Abstract] OR "
                    f"'Tricuspid Valve'[Title/Abstract]) AND ({date_range}[Date - Publication])")
    
    try:
        handle = Entrez.esearch(db="pubmed", term=search_query, retmax=10)
        record = Entrez.read(handle)
        ids = record["IdList"]
        handle.close()
        
        if not ids:
            return ""
            
        handle = Entrez.efetch(db="pubmed", id=",".join(ids), rettype="abstract", retmode="text")
        abstracts = handle.read()
        handle.close()
        return abstracts
    except Exception as e:
        print(f"PubMed retrieval error: {e}")
        return ""

def generate_valve_summary(pubmed_data):
    """Combines PubMed abstracts with a live Google Search for a full synthesis."""
    client = genai.Client(api_key=GEMINI_KEY)
    
    # Prompt instructs Gemini to use the provided data AND its search tool
    search_query = f"""
    You are a Cardiac Surgery Research Assistant. 
    
    1. Review these provided PubMed abstracts: 
    {pubmed_data}
    
    2. Use your search tool to find any OTHER major news or trials from the last 7 days 
    in JACC, NEJM, Circulation, and The Lancet regarding TAVR/SAVR and Mitral/Tricuspid interventions.
    
    Focus on clinical implications (e.g., reintervention rates, mortality, and patient surveillance).
    
    CRITICAL: Provide clickable hyperlinks using Markdown: [Article Title](URL).
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=search_query,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.0
            )
        )
        return response.text if response.text.strip() else None
    except Exception as e:
        print(f"Generation error: {e}")
        return None

def send_valve_report(report_body):
    """Sends the report only if content was generated."""
    if not report_body:
        print("No content found for this week. Skipping email.")
        return

    msg = EmailMessage()
    msg['Subject'] = f"Weekly Valve & Structural Heart Update: {time.strftime('%Y-%m-%d')}"
    msg['From'] = MY_EMAIL
    msg['To'] = MY_EMAIL

    html_content = report_body.replace('\n', '<br>')
    msg.set_content(report_body)
    msg.add_alternative(f"""
    <html>
      <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #0047AB;">Valve Research & Clinical Brief</h2>
        <hr>
        <div style="white-space: pre-wrap;">{html_content}</div>
        <hr>
        <p style="font-size: 0.8em; color: #777;">Automated Clinical Research Agent</p>
      </body>
    </html>
    """, subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(MY_EMAIL, EMAIL_PASS)
            smtp.send_message(msg)
        print("Valve Research Email sent successfully!")
    except Exception as e:
        print(f"Email delivery failed: {e}")

if __name__ == "__main__":
    print("Fetching direct PubMed data...")
    pubmed_text = fetch_pubmed_valves()
    
    print("Generating clinical synthesis...")
    report = generate_valve_summary(pubmed_text)
    
    send_valve_report(report)
