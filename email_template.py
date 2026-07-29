"""
email_template.py — Smart personalized email builder.

Generates a clean, professional email body for each recruiter
with company-specific lines injected automatically.
"""

# -----------------------------------------------------------------
# Company-specific one-liner reasons (used in the "I am particularly
# drawn to [Company]..." sentence). Add more as needed.
# -----------------------------------------------------------------
COMPANY_HIGHLIGHTS = {
    "Amazon":                      "your relentless focus on scalability and your pioneering work in cloud infrastructure through AWS",
    "Uber":                        "your commitment to solving large-scale distributed systems problems and your culture of engineering excellence",
    "Broadridge":                  "your leadership in financial technology and your investment in modernising capital markets infrastructure",
    "NTT Data":                    "your global footprint in digital transformation and managed services",
    "HCL Tech":                    "your expansive engineering culture and emphasis on innovation-led growth",
    "HCL Talentcare":              "your people-first approach and strong talent development ecosystem",
    "GlobalLogic":                 "your product engineering expertise and collaborative approach to building world-class software",
    "Mphasis":                     "your focus on cognitive computing and hyper-personalised digital solutions",
    "Tech Mahindra":               "your commitment to next-generation digital transformation and connected experiences",
    "Tata Technologies":           "your strong legacy in engineering and manufacturing IT services",
    "Tata Advanced Systems Limited": "your pioneering work in defence and aerospace technology solutions",
    "Genpact":                     "your data-driven approach to process transformation and AI-led services",
    "Sutherland Global":           "your AI-powered business process solutions and culture of continuous innovation",
    "Fujitsu":                     "your global leadership in digital transformation and your co-creation philosophy",
    "Atos":                        "your commitment to decarbonisation and digital sovereignty at scale",
    "Cyient":                      "your expertise at the intersection of engineering and technology services",
    "IBS Software":                "your deep domain expertise in aviation and travel technology",
    "Infosys / GUVI":              "your mission to make quality tech education accessible across India",
    "Juspay / GUVI":               "your mission to make quality tech education accessible across India",
    "Just Dial":                   "your scale as India's largest local search platform and your data-rich engineering challenges",
    "United Health Group":         "your mission to help people live healthier lives through technology",
    "Inrhythm Solutions":          "your agile-first culture and expertise in digital product engineering",
    "MAQ Software":                "your data analytics and Power BI expertise and your record of delivering high-impact business intelligence solutions",
    "QED Baton":                   "your talent-matching platform and commitment to building world-class engineering teams",
    "Calsoft":                     "your product engineering capabilities in storage, networking, and cloud",
    "TekSystems":                  "your reputation for placing top engineering talent and your strong staffing network",
    "Impelsys":                    "your innovation in digital learning and content technology",
    "Commlab":                     "your expertise in rapid e-learning solutions and instructional design",
    "Miracle Software":            "your strength in enterprise integrations and digital transformation consulting",
    "Pratian Technologies":        "your agile engineering culture and product-mindset approach to software delivery",
    "Zen Technologies":            "your focus on defence simulation and training technology",
    "ZenQ":                        "your quality-first culture and expertise in independent software testing",
    "Technovert":                  "your cloud-native and digital solutions practice",
    "Safran (Morpho Group)":       "your leadership in identity and security technology",
    "Rane Group":                  "your heritage in precision auto-components and emerging investments in automotive software",
    "Energy Infratech":            "your work at the intersection of energy and digital infrastructure",
    "Effectronics":                "your expertise in defence electronics and embedded systems",
    "Vem Technologies":            "your solutions in IT consulting and workforce management",
    "Intone Networks":             "your RPA and intelligent automation capabilities",
    "Incessant Technologies":      "your focus on digital transformation and platform engineering",
    "Mold Tek Technologies":       "your innovative work in packaging technology and industrial automation",
    "Osmosys Software Solutions":  "your full-stack product development expertise and your collaborative engineering culture",
    "Epic Research":               "your data-driven investment research platform",
    "Excers":                      "your technology services and your focus on delivering value-driven solutions",
    "Globussoft":                  "your web and mobile product development expertise",
    "Aptroid Technologies":        "your interactive digital experience solutions",
    "CEI America":                 "your engineering consulting and technical staffing expertise",
    "Grey Campus":                 "your commitment to professional development and technology certification training",
    "CallHealth":                  "your mission to transform healthcare delivery through technology",
    "Sterling & Wilson":           "your renewable energy and solar EPC capabilities",
    "Ramtech":                     "your IT solutions and consulting expertise",
    "Cybage":                      "your product engineering and QA services with a focus on innovation",
    "Alliance Global Services":    "your IT staffing and consulting expertise and your wide industry reach",
    "UXReactor":                   "your human-centred design philosophy and your product strategy work",
    "Cruiseline Ship Management":  "your unique work at the crossroads of maritime operations and digital technology",
    "Intelenet Global":            "your BPM and digital transformation solutions",
    "Broadridge":                  "your financial technology leadership and commitment to investor communications innovation",
    "Pubmatic":                    "your programmatic advertising infrastructure and engineering-first culture",
}

DEFAULT_HIGHLIGHT = "your innovative work and the impactful engineering challenges your team is solving"

SUBJECT = "Application for Backend Engineering / AI-ML Role – Gokulakannan B S"

SENDER_INFO = {
    "name":     "Gokulakannan B S",
    "phone":    "9444520998",
    "linkedin": "https://www.linkedin.com/in/bsgk/",
    "github":   "https://github.com/gokul3177",
    "leetcode": "https://leetcode.com/u/gokul3177/",
    "email":    "gokulakannanbs31@gmail.com",
}


PREFIXES = {"mr", "mr.", "ms", "ms.", "mrs", "mrs.", "dr", "dr."}

def _greeting(hr_name: str | None) -> str:
    if not hr_name:
        return "Dear Hiring Team,"
    parts = hr_name.strip().split()
    if parts and parts[0].lower() in PREFIXES:
        parts = parts[1:]
    if not parts:
        return "Dear Hiring Team,"
    first = parts[0]
    return f"Dear {first},"


def build_email(company: str, hr_name: str | None) -> tuple[str, str]:
    """
    Returns (subject, plain_text_body) for the given company/HR.
    """
    greeting = _greeting(hr_name)
    s = SENDER_INFO

    body = f"""{greeting}

I am a final-year Computer Science undergraduate at SASTRA University looking for Backend Engineering or AI/ML roles at {company} (available from Jan 2027 for internship / full-time).

Key Highlights:
- Amazon ML Summer School 2025: Selected nationally for advanced GenAI, LLM/RAG, and System Design training.
- Core Projects: Engineered LukMatch (LLM semantic matching), LukBill (NLP medical invoice automation), and LukWealth (PostgreSQL, Docker, CI/CD).
- Technical Core: Python, REST APIs, SQL (PostgreSQL, MySQL), NoSQL (MongoDB), Docker, AWS, Git.
- Problem Solving: Solved 250+ DSA problems on LeetCode; Core Member of SASTRA Robotics Club.

I would love the opportunity to discuss how my technical skills align with engineering opportunities at {company}. My resume is attached for your review.

Best regards,
{s['name']}
Phone    : +91 {s['phone']}
LinkedIn : {s['linkedin']}
GitHub   : {s['github']}
LeetCode : {s['leetcode']}
Email    : {s['email']}
"""
    return SUBJECT, body.strip()
