import os
import datetime
from Bio import Entrez
from google import genai

Entrez.email = "jrj023@gmail.com" 
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

def fetch_dnp_research():
    today = datetime.date.today()
    # Looking back 30 days for DNP research to ensure we don't miss deeper studies
    last_month = today - datetime.timedelta(days=30)
    date_range = f"{last_month.strftime('%Y/%m/%d')}:{today.strftime('%Y/%m/%d')}"

    # Target keywords: Surveillance, KCCQ, Asymptomatic AS, Biomarkers
    search_query = (
        f"(('Aortic Stenosis'[Title/Abstract]) AND ('Asymptomatic'[Title/Abstract])) OR "
        f"('KCCQ'[Title/Abstract]) OR ('Quality of Life'[Title/Abstract] AND 'TAVR'[Title/Abstract]) OR "
        f"('Pro-BNP'[Title/Abstract] AND 'Aortic Stenosis'[Title/Abstract]) "
        f"AND ({date_range}[Date - Publication])"
    )

    handle = Entrez.esearch(db="pubmed", term=search_query, retmax=5)
    record = Entrez.read(handle)
    ids = record["IdList"]
    handle.close()

    if not ids: return None

    handle = Entrez.efetch(db="pubmed", id=",".join(ids), rettype="abstract", retmode="text")
    abstract_data = handle.read()
    handle.close()
    return abstract_data

def generate_dnp_synthesis(text):
    if not text: return "No new specific DNP-related studies found this month."
    
    client = genai.Client(api_key=GEMINI_KEY)
    prompt = f"""
    You are a Doctoral Nursing Research Assistant. 
    Analyze these abstracts for a DNP Project focused on Aortic Stenosis Surveillance and Patient Outcomes (KCCQ).
    
    Categorize the findings into:
    1. **Evidence for Surveillance**: New data on timing of intervention or biomarkers (Pro-BNP).
    2. **Patient-Reported Outcomes**: Specifically any mention of KCCQ or quality of life.
    3. **Clinical Practice Gap**: Does this study highlight a need for better protocols?
    4. **DNP Project Synthesis**: One paragraph summarizing how this helps support a nurse-led surveillance protocol.

    Abstracts:
    {text}
    """
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text

if __name__ == "__main__":
    data = fetch_dnp_research()
    report = generate_dnp_synthesis(data)
    print(report)
    import smtplib
import os
from email.message import EmailMessage

def send_dnp_summary(report_content):
    msg = EmailMessage()
    msg.set_content(report_content)
    
    # Custom subject for your DNP studies
    msg['Subject'] = "DNP Research Agent: Weekly Literature Update"
    msg['From'] = f"DNP Agent <{os.environ.get('MAIL_USERNAME')}>"
    msg['To'] = os.environ.get('MAIL_USERNAME')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(os.environ.get('MAIL_USERNAME'), os.environ.get('MAIL_PASSWORD'))
            smtp.send_message(msg)
        print("DNP Research Email sent successfully!")
    except Exception as e:
        print(f"Email failed: {e}")

# Trigger the email at the end of the script
# Replace 'final_output' with the actual variable name used in your script
send_dnp_summary(final_output)
