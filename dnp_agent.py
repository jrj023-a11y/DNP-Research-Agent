import os
import datetime
from Bio import Entrez
from google import genai
import smtplib
from email.message import EmailMessage

Entrez.email = "jrj023@gmail.com"
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

def fetch_dnp_research():
    today = datetime.date.today()
    last_month = today - datetime.timedelta(days=30)
    date_range = f"{last_month.strftime('%Y/%m/%d')}:{today.strftime('%Y/%m/%d')}"
    
    search_query = (f"(('Aortic Stenosis'[Title/Abstract]) AND ('Asymptomatic'[Title/Abstract])) OR "
                    f"('KCCQ'[Title/Abstract]) OR ('Quality of Life'[Title/Abstract] AND 'TAVR'[Title/Abstract]) OR "
                    f"('Pro-BNP'[Title/Abstract] AND 'Aortic Stenosis'[Title/Abstract]) "
                    f"AND ({date_range}[Date - Publication])")
    
    handle = Entrez.esearch(db="pubmed", term=search_query, retmax=5)
    record = Entrez.read(handle)
    ids = record["IdList"]
    handle.close()

    if not ids:
        return None

    handle = Entrez.efetch(db="pubmed", id=",".join(ids), rettype="abstract", retmode="text")
    abstract_data = handle.read()
    handle.close()
    return abstract_data

def generate_dnp_synthesis(text):
    if not text:
        return "No new specific DNP-related studies found this month."
    
    client = genai.Client(api_key=GEMINI_KEY)
    
    # Prompt updated to request HTML Hyperlinks
    prompt = f"""
    You are a Doctoral Nursing Research Assistant. Analyze these abstracts for a DNP Project focused on Aortic Stenosis Surveillance and Patient Outcomes (KCCQ).
    
    IMPORTANT: For every study mentioned, you MUST provide the title as an HTML hyperlink using its DOI or PubMed URL. 
    Example: <a href="https://pubmed.ncbi.nlm.nih.gov/ID">Study Title</a>
    
    Format the response using HTML tags (like <b>, <ul>, and <li>) instead of Markdown.
    
    Categorize the findings into:
    1. Evidence for Surveillance
    2. Patient-Reported Outcomes (KCCQ focus)
    3. Clinical Practice Gap
    4. DNP Project Synthesis (One paragraph)

    Abstracts: {text}
    """
    
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text

def send_dnp_summary(report_content):
    msg = EmailMessage()
    
    # Set the email to be sent as HTML
    msg.set_content("Please use an HTML-compliant email client to view this report.")
    msg.add_alternative(report_content, subtype='html')
    
    msg['Subject'] = "DNP Research Agent: Weekly Literature Update"
    msg['From'] = f"DNP Agent <{os.environ.get('MAIL_USERNAME')}>"
    msg['To'] = os.environ.get('MAIL_USERNAME')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(os.environ.get('MAIL_USERNAME'), os.environ.get('MAIL_PASSWORD'))
            smtp.send_message(msg)
        print("DNP Research Email (HTML) sent successfully!")
    except Exception as e:
        print(f"Email failed: {e}")

if __name__ == "__main__":
    data = fetch_dnp_research()
    report = generate_dnp_synthesis(data)
    print(report)
    
    # Final trigger using the correct variable 'report'
    send_dnp_summary(report)
