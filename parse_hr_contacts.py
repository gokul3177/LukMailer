"""
parse_hr_contacts.py — Parses contacts/hr_details_contact.csv and outputs contacts_hr.py
"""

import pandas as pd
import re

def clean_str(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    # clean unprintable / unicode junk
    s = re.sub(r'[\xa0\x00-\x1f\x7f-\x9f]', ' ', s)
    return ' '.join(s.split())

def main():
    df = pd.read_excel(r'E:\Lukmailer\contacts\hr_details_contact.csv')
    data = df.iloc[1:] # row 0 is header
    
    recruiters = []
    seen_emails = set()

    for idx, row in data.iterrows():
        company = clean_str(row.iloc[0])
        hr_name = clean_str(row.iloc[1])
        email = clean_str(row.iloc[2]).lower()

        if not email or '@' not in email:
            print(f"Skipping row {idx}: no valid email ('{email}')")
            continue

        if email in seen_emails:
            print(f"Skipping duplicate email '{email}' at row {idx}")
            continue

        seen_emails.add(email)
        
        # Clean company name trailing commas
        company = company.rstrip(',').strip()
        
        # If hr_name is generic placeholder, treat as None
        if hr_name in ['AMCAT', 'AMCAT ']:
            hr_name = None

        recruiters.append((company, hr_name, email))

    print(f"Extracted {len(recruiters)} unique HR contacts.")

    with open(r'E:\Lukmailer\contacts_hr.py', 'w', encoding='utf-8') as f:
        f.write('"""\ncontacts_hr.py -- HR recruiter contacts parsed from contacts/hr_details_contact.csv\n"""\n\n')
        f.write('RECRUITERS = [\n')
        for company, hr_name, email in recruiters:
            hr_repr = f'"{hr_name}"' if hr_name else 'None'
            f.write(f'    ("{company}", {hr_repr}, "{email}"),\n')
        f.write(']\n')

    print("Successfully generated contacts_hr.py")

if __name__ == '__main__':
    main()
