"""
backend/email_generator.py — Smart personalized email builder for LukMailer.

Generates company-tailored subject lines and body text with customizable templates.
"""

from backend.config import (
    DEFAULT_SENDER_NAME,
    DEFAULT_SENDER_PHONE,
    DEFAULT_SENDER_LINKEDIN,
    DEFAULT_SENDER_GITHUB,
    DEFAULT_SENDER_LEETCODE,
)

# Company-specific highlights dictionary (Deduplicated)
COMPANY_HIGHLIGHTS = {
    "Amazon": "your relentless focus on scalability and your pioneering work in cloud infrastructure through AWS",
    "Uber": "your commitment to solving large-scale distributed systems problems and your culture of engineering excellence",
    "Broadridge": "your financial technology leadership and commitment to investor communications innovation",
    "NTT Data": "your global footprint in digital transformation and managed services",
    "HCL Tech": "your expansive engineering culture and emphasis on innovation-led growth",
    "HCL Talentcare": "your people-first approach and strong talent development ecosystem",
    "GlobalLogic": "your product engineering expertise and collaborative approach to building world-class software",
    "Mphasis": "your focus on cognitive computing and hyper-personalised digital solutions",
    "Tech Mahindra": "your commitment to next-generation digital transformation and connected experiences",
    "Tata Technologies": "your strong legacy in engineering and manufacturing IT services",
    "Tata Advanced Systems Limited": "your pioneering work in defence and aerospace technology solutions",
    "Genpact": "your data-driven approach to process transformation and AI-led services",
    "Sutherland Global": "your AI-powered business process solutions and culture of continuous innovation",
    "Fujitsu": "your global leadership in digital transformation and your co-creation philosophy",
    "Atos": "your commitment to decarbonisation and digital sovereignty at scale",
    "Cyient": "your expertise at the intersection of engineering and technology services",
    "IBS Software": "your deep domain expertise in aviation and travel technology",
    "Infosys / GUVI": "your mission to make quality tech education accessible across India",
    "Juspay / GUVI": "your mission to make quality tech education accessible across India",
    "Just Dial": "your scale as India's largest local search platform and your data-rich engineering challenges",
    "United Health Group": "your mission to help people live healthier lives through technology",
    "Inrhythm Solutions": "your agile-first culture and expertise in digital product engineering",
    "MAQ Software": "your data analytics and Power BI expertise and your record of delivering high-impact business intelligence solutions",
    "QED Baton": "your talent-matching platform and commitment to building world-class engineering teams",
    "Calsoft": "your product engineering capabilities in storage, networking, and cloud",
    "TekSystems": "your reputation for placing top engineering talent and your strong staffing network",
    "Impelsys": "your innovation in digital learning and content technology",
    "Commlab": "your expertise in rapid e-learning solutions and instructional design",
    "Miracle Software": "your strength in enterprise integrations and digital transformation consulting",
    "Pratian Technologies": "your agile engineering culture and product-mindset approach to software delivery",
    "Zen Technologies": "your focus on defence simulation and training technology",
    "ZenQ": "your quality-first culture and expertise in independent software testing",
    "Technovert": "your cloud-native and digital solutions practice",
    "Safran (Morpho Group)": "your leadership in identity and security technology",
    "Rane Group": "your heritage in precision auto-components and emerging investments in automotive software",
    "Energy Infratech": "your work at the intersection of energy and digital infrastructure",
    "Effectronics": "your expertise in defence electronics and embedded systems",
    "Vem Technologies": "your solutions in IT consulting and workforce management",
    "Intone Networks": "your RPA and intelligent automation capabilities",
    "Incessant Technologies": "your focus on digital transformation and platform engineering",
    "Mold Tek Technologies": "your innovative work in packaging technology and industrial automation",
    "Osmosys Software Solutions": "your full-stack product development expertise and your collaborative engineering culture",
    "Epic Research": "your data-driven investment research platform",
    "Excers": "your technology services and your focus on delivering value-driven solutions",
    "Globussoft": "your web and mobile product development expertise",
    "Aptroid Technologies": "your interactive digital experience solutions",
    "CEI America": "your engineering consulting and technical staffing expertise",
    "Grey Campus": "your commitment to professional development and technology certification training",
    "CallHealth": "your mission to transform healthcare delivery through technology",
    "Sterling & Wilson": "your renewable energy and solar EPC capabilities",
    "Ramtech": "your IT solutions and consulting expertise",
    "Cybage": "your product engineering and QA services with a focus on innovation",
    "Alliance Global Services": "your IT staffing and consulting expertise and your wide industry reach",
    "UXReactor": "your human-centred design philosophy and your product strategy work",
    "Cruiseline Ship Management": "your unique work at the crossroads of maritime operations and digital technology",
    "Intelenet Global": "your BPM and digital transformation solutions",
    "Pubmatic": "your programmatic advertising infrastructure and engineering-first culture",
}

DEFAULT_HIGHLIGHT = "your innovative work and the impactful engineering challenges your team is solving"
DEFAULT_SUBJECT = "Application for Backend Engineering / AI-ML Role – {sender_name}"

PREFIXES = {"mr", "mr.", "ms", "ms.", "mrs", "mrs.", "dr", "dr."}

def format_greeting(hr_name: str | None) -> str:
    """Format greeting line based on HR name."""
    if not hr_name or not hr_name.strip():
        return "Dear Hiring Team,"
    parts = hr_name.strip().split()
    if parts and parts[0].lower() in PREFIXES:
        parts = parts[1:]
    if not parts:
        return "Dear Hiring Team,"
    first = parts[0].capitalize()
    return f"Dear {first},"

def get_company_highlight(company: str) -> str:
    """Lookup company specific highlight or return default."""
    return COMPANY_HIGHLIGHTS.get(company.strip(), DEFAULT_HIGHLIGHT)

def build_email_template(
    company: str,
    hr_name: str | None = None,
    sender_info: dict | None = None,
    custom_subject: str | None = None,
    custom_body: str | None = None,
) -> tuple[str, str]:
    """
    Builds (subject, plain_text_body) for a recruiter contact.
    """
    merged = {
        "name": DEFAULT_SENDER_NAME or "Your Name",
        "phone": DEFAULT_SENDER_PHONE or "",
        "linkedin": DEFAULT_SENDER_LINKEDIN or "",
        "github": DEFAULT_SENDER_GITHUB or "",
        "leetcode": DEFAULT_SENDER_LEETCODE or "",
        "email": "",
    }
    if sender_info:
        merged.update({k: v for k, v in sender_info.items() if v})
    s = merged

    greeting = format_greeting(hr_name)
    company_clean = company.strip() if company else "your esteemed organization"

    # Subject
    if custom_subject:
        subject = custom_subject.replace("{company}", company_clean).replace("{sender_name}", s["name"])
    else:
        subject = DEFAULT_SUBJECT.format(sender_name=s["name"])

    # Body
    if custom_body:
        body = custom_body \
            .replace("{greeting}", greeting) \
            .replace("{company}", company_clean) \
            .replace("{sender_name}", s["name"]) \
            .replace("{sender_phone}", s.get("phone", "")) \
            .replace("{sender_linkedin}", s.get("linkedin", "")) \
            .replace("{sender_github}", s.get("github", "")) \
            .replace("{sender_leetcode}", s.get("leetcode", "")) \
            .replace("{sender_email}", s.get("email", ""))
    else:
        highlight = get_company_highlight(company_clean)
        body = f"""{greeting}

I am writing to express my interest in engineering opportunities at {company_clean}. I am excited about {highlight}.

[Write your introduction and key highlights here. Describe your background, skills, and what makes you a strong candidate.]

Key Highlights:
- [Highlight 1 — e.g., a major achievement or certification]
- [Highlight 2 — e.g., a key project you built]
- [Highlight 3 — e.g., your technical skills]

I would love the opportunity to discuss how my background aligns with the team at {company_clean}. My resume is attached for your review.

Best regards,
{s['name']}"""
        # Append contact details only if provided
        if s.get('phone'):
            body += f"\nPhone    : {s['phone']}"
        if s.get('linkedin'):
            body += f"\nLinkedIn : {s['linkedin']}"
        if s.get('github'):
            body += f"\nGitHub   : {s['github']}"
        if s.get('leetcode'):
            body += f"\nLeetCode : {s['leetcode']}"
        if s.get('email'):
            body += f"\nEmail    : {s['email']}"

    return subject, body.strip()
