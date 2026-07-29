"""
fast_filter.py - Quick MX-only check on contacts_wave2.py
Removes contacts whose email domain has no MX record.
Saves clean list back to contacts_wave2.py and prints report.
"""
import dns.resolver
from contacts_wave2 import RECRUITERS

def has_mx(domain):
    try:
        dns.resolver.resolve(domain, "MX", lifetime=4)
        return True
    except Exception:
        return False

valid, invalid = [], []
seen_domains = {}

print(f"Fast MX check on {len(RECRUITERS)} contacts...")

for entry in RECRUITERS:
    company, hr_name, email = entry
    domain = email.split("@")[1].lower()
    if domain not in seen_domains:
        seen_domains[domain] = has_mx(domain)
    if seen_domains[domain]:
        valid.append(entry)
    else:
        invalid.append(entry)
        print(f"  [REMOVED] {email} -- no MX record for {domain}")

print(f"\n[OK] Valid : {len(valid)}")
print(f"[REMOVED] Invalid: {len(invalid)}")

# Overwrite contacts_wave2.py with only valid entries
with open("contacts_wave2.py", "w", encoding="utf-8") as f:
    f.write('"""\ncontacts_wave2.py -- Wave 2 contacts (MX-filtered)\n"""\n\nRECRUITERS = [\n')
    for company, hr_name, email in valid:
        hr_str = f'"{hr_name}"' if hr_name else "None"
        f.write(f'    ("{company}", {hr_str}, "{email}"),\n')
    f.write("]\n")

print(f"\ncontacts_wave2.py updated -- {len(valid)} clean contacts ready to send.")
