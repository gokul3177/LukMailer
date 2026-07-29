"""
parse_csv.py — Parses getContacts.csv and generates contacts_wave2.py + 2ndWave.txt
Run once: python parse_csv.py
"""

import re

RAW = """Sourabh|Kane|sourabh.kane@pvcleanmobility.com
Pawan|Kumar|pawan.kumar@autofitltd.com
Dora|Srivalli|srivallid@pisquaretech.com
Khushboo|Sidana|khushboo.sidana@anandgroupindia.com
Shweta|Bansal|shweta.bansal@makinoindia.com
Prajna|Jain|prajna.jain@bluehyundai.co.in
Vishakha|Mogral|vishakha.mogral@ultraviolette.com
Anubhav|Pathak|anubhav.pathak@continental-engines.com
Prabhat|Sharma|prabhat.sharma@tccimfg.in
Dnyaneshwar|Rathod|dnyaneshwar.rathod@varroc.com
Jaywant|Solankar|jaywant.solankar@reliableautotech.com
Omkar|Lokhande|omkar.lokhande@gns-india.com
Nithya|Reddy|nithya@saabengg.com
Sunil|Sharma|sunil.sharma@bmw-deutschemotoren.in
Amit|Singh|aksingh@in.nifco.com
JK|Sahu|jk.sahu@pravaig.com
Happy|Bhati|happy@omegaseikimobility.com
Kapil|Rana|kapil@omegaseikimobility.com
Sanjay|Lamba|sanjaylamba@bestex.co.in
Nikhil|Kumar|nikhil.kumar@electraev.com
Anand|R|anand.pr@lismail.in
Mamta|Singh|mamta.singh@konceptmahindra.com
Feeba||f@mahavirauto.com
Deepak|Kapoor|deepak@wasantoyotamumbai.com
Ashutosh|Sinha|ashutosh.sinha@wiggles.in
Pearl||pearl@pearlpet.net
Sakshi|Converse|sakshi@conversejob.com
Tanusree|Chanda|tanusree.chanda@wiggles.in
Jaya|Parmar|jaya@thehelloworld.com
Manjusha|Manne|manjusha.manne@dbsmintek.com
Winny|Department|departmentw@winnyimmigration.com
Divya|Singh|divya.singh@tumbledry.in
Sukirti|Garg|sukirtilovespets@supertails.com
Mayuri|Kothavle|mayuri.kothavle@stockholdingdms.com
Rakesh|Salvi|rakesh.salvi@yadavmeasurements.com
Karen|Lobo|karen@thehelloworld.com
Srikala|Pillai|srikala@coutloot.com
Vishant|Jadhav|vishant.jadhav@wiggles.in
Gunjan|Singh|gunjan@wiggles.in
Pallavi|Bhatnagar|pallavi@conversejob.com
Deepti|Verma|deepti@laundryheap.co.uk
Pratiksha|Patole|ppatole@mtpl.org
Miloni|Patil|miloni.patil@startv.com
Bijoy|Francis|bijoy.francis@eliteindia.com
Poojashree|R|poojashree.r@skillslash.com
Rajni|Vaid|r.vaid@infonativesolutions.com
Ruchika|Parikh|ruchika.parikh@phibonacci.com
Nikhil|Sharma|nikhil.sharma@dbmi.edu.in
Venkatesh||venkatesh@eluminaelearning.com.au
Navya|Vadada|navya@whizlabs.com
Melissa|Pai|melissa@jigsawacademy.com
Ishaa|Shah|ishaa.shah@mentoria.com
Arshi|Dahma|arshi@innovalance.com
Siddharth|Dahma|siddharth.dahma@edfora.com
Shalini|Malhotra|shalini.m@classteacher.com
Amitha|Rajendran|amitha@squarepanda.com
Urvashi|Jibhkate|urvashi.j@paradisosolutions.com
Neha|Gupta|neha@suraasa.com
Naman|Joshi|naman@codekaroyaaro.com
Arijit|Purkayastha|ap@infonative.net
Jeffisha|GR|jeffisha.gr@purpletutor.com
Divya|Nain|divya@mindcypress.org
Pooja|Gupta|pooja.gupta@vaidikedu.com
Shreya|Raka|shreya.raka@purpletutor.com
Surender|Kumar|surender@classteacher.com
Minolette|Lemos|minolette@squarepanda.com
Shipra|Grover|sgrover@apparelresources.com
Charu|Singhvi|charu.singhvi@beyoung.in
Chitra|Dhar|chitra.dhar@coats.com
Heena|Raina|heena@menrocks.in
Kasturi|Choudhury|kasturi@neemans.com
Hedwig|Kerketta|hedwig@usplworld.com
Shruti|Vig|shruti.vig@john-jacobs.com
Rajeev|Kumar|rajeev.kumar@sabsexports.com
Trupti|Bansode|trupti.bansode@mirraw.com
Rajiv|Sharma|hrd@gimatex.co.in
Dhana|Sekar|dhana.sekar@maxwellindustries.com
Charu|Vats|charu.vats@fablestreet.com
Pujan|Majumdar|pujan@bombayshirts.com
Sneha|Singh|snehasingh@myblissclub.in
Prajakta|Dalvi|prajakta@teamhgs.com
Sana|Daniel|sana.daniel@faballey.com
Anjan|Ribadiya|anjan@neemans.com
Alice|George|alice.george@vstar.in
Mitul|Patel|mitul@condorinblu.com
Drishti|Jain|drishti@beyoung.in
Sankar|Shanmugam|sankar@celebritygroup.com
Keerthana|Aniyan|keerthana@myblissclub.in
Bharathi|R|bharathi@outshiny.com
Harish|Dalal|harish.dalal@aqualiteindia.com
Sahithi|Vasantharao|sahithi@suta.in
Reegan|A|reegan.a@classicpolos.com
Aman|Mehta|aman.mehta@geniemode.com
Ajay|Bhatia|ajay@evelineinternational.com
Kuldeep|Yadav|kuldeep@leinershoes.com
Shivani|Maidham|shivani.maidham@mirraw.com
Manjula|Soorve|manjula@neemans.com
Ruchi|Verma|ruchi.verma@ampm.in
Jagan|Durai|jagan@srinivasafashions.com
Shivani|Saini|shivani.saini@taruntahiliani.com
Ankita|Raj|ankita@neemans.com
Saurav|Kumar|saurav@lecoanethemant.com
Dipak|Mehata|dipak@magnoliablossom.com
Khushboo|Shrivastava|khushboo.s@ixfi.com
Nishith|Shetty|hrmumbai@basizfa.com
Pooja|Gupta|pooja.gupta@aristotleconsultancy.com
Kanika|Sharma|kanikas@smcinvestments.co.in
Siddhi|Palekar|siddhi@numadic.com
Rachana|Kokate|rachana.kokate@definedge.com
Priyanka|S|priyanka@thegrowtharrow.com
Careers|Pinnacle|careers.pinnaclefinancial@pnfp.com
Sathya|Mayalagu|sathya.m@jiraaf.com
Adnan|Khan|adnan.khan@smartowner.com
Manisha|Rajput|manisha.rajput@clxns.in
Harshal|Shah|harshal@fno.co
Puja|Chakraborty|puja@surfboard.se
Ayushi|Soni|ayushi.soni@finwaycapital.in
Shradha|Lawande|shradha@moneyhop.co
Muthukumar|HRD|hrd@shriramfinance.in
Adhya|Shinde|adhya.shinde@mangalkeshav.com
Juhi|Trivedi|juhitrivedi@sunidhi.com
Roma|Rasal|rrasal@technoworld.in
Nachiket|Ingale|nachiket.ingale@bourkegroup.com.au
"""

def domain_to_company(email: str) -> str:
    domain = email.split("@")[1].split(".")[0]
    return domain.replace("-", " ").title()

lines = [l.strip() for l in RAW.strip().splitlines() if l.strip()]

recruiters = []
txt_lines  = []

for line in lines:
    parts = line.split("|")
    if len(parts) < 3:
        continue
    first, last, email = parts[0].strip(), parts[1].strip(), parts[2].strip()
    if not email or "@" not in email:
        continue
    hr_name = f"{first} {last}".strip()
    company = domain_to_company(email)
    recruiters.append((company, hr_name, email))
    txt_lines.append(f"{company} | {hr_name} | {email}")

# ── Write 2ndWave.txt ──────────────────────────────────────────
with open("2ndWave.txt", "w", encoding="utf-8") as f:
    f.write("# Wave 2 Contacts\n")
    f.write(f"# Total: {len(recruiters)}\n")
    f.write("# Format: Company | HR Name | Email\n\n")
    f.write("\n".join(txt_lines))
print(f"[OK] 2ndWave.txt written -- {len(recruiters)} contacts")

# -- Write contacts_wave2.py -----------------------------------------------
with open("contacts_wave2.py", "w", encoding="utf-8") as f:
    f.write('"""\ncontacts_wave2.py -- Wave 2 recruiter contacts (auto-generated from getContacts.csv)\nEach entry: (company, hr_name_or_none, email)\n"""\n\n')
    f.write("RECRUITERS = [\n")
    for company, hr_name, email in recruiters:
        hr_str = f'"{hr_name}"' if hr_name else "None"
        f.write(f'    ("{company}", {hr_str}, "{email}"),\n')
    f.write("]\n")
print(f"[OK] contacts_wave2.py written -- {len(recruiters)} entries")
print(f"\nRun verification next:\n  python verify_emails.py --wave2")
