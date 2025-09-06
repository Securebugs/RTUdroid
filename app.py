from flask import Flask, Response, request, jsonify
import uuid
import time
import requests
from urllib.parse import urlparse

app = Flask(__name__)

@app.route('/')
def index():
    # Syllabus data from provided list
    syllabus_data = [
        {"branch": "B.Tech First Year", "session": "2009-10", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/First_Year_Syllabus_8-7-09.pdf"},
        {"branch": "B.Tech First Year", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/First_year_scheme_and_syllabus_effective_from_2012-13n11.pdf"},
        {"branch": "B.Tech First Year", "session": "2019-20 Onwards", "link": "https://rtu.ac.in/home/wp-content/uploads/2020/07/Syllabus-I-Year-2019-20-onwards.pdf"},
        {"branch": "B.Tech First Year", "session": "2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/07/Syllabus-I-Year.pdf"},
        {"branch": "B.Tech First Year (Revised)", "session": "2017-18", "link": "https://rtu.ac.in/home/wp-content/uploads/2017/08/Syllabus_B.Tech_._I_Year__2017-18__17.08.2017.pdf"},
        {"branch": "Old First Year Annual Scheme", "session": "2006-07", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/syllabus_I_BE_all.pdf"},
        {"branch": "Aeronautical Engineering", "session": "2011-12", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/B_Tech_aeronautical_Syllabus.pdf"},
        {"branch": "Aeronautical Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech_Aero_3-8sem-syll.pdf"},
        {"branch": "Aeronautical Engineering", "session": "2017-18 and 2018-19 III Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/Syllabus_Aero_RTU.pdf"},
        {"branch": "Aeronautical Engineering", "session": "2017-18 and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/02/Syllabus-Aeronautical-Engg.pdf"},
        {"branch": "Aeronautical Engineering", "session": "2019-20 V to VI", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/AN.pdf"},
        {"branch": "Agricultural Engineering", "session": "2016-17 onwards V-VIII Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2017/07/Ag.-Engg.-Syllabus-B.Tech-V-to-VIII-sem.pdf"},
        {"branch": "Agricultural Engineering", "session": "2016-17 (odd semester) onwards III & IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2016/07/Syllabus-III-IV-Sem.-Agricultural-Engineering.pdf"},
        {"branch": "Agricultural Engineering", "session": "2017-18 and 2018-19 III Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/Final-Syallabus-from-II-Year-B-Tech.pdf"},
        {"branch": "Agricultural Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/Syallabus-AG-Engg..pdf"},
        {"branch": "Agricultural Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/AG.pdf"},
        {"branch": "Applied Electronics & Instrumentation", "session": "2009-10", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/Syllabus-B.Tech-Applied-Electronics-and-Instrumentation-old.pdf"},
        {"branch": "Applied Electronics & Instrumentation", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/Syllabus-B.Tech-Applied-Electronics-and-Instrumentation.pdf"},
        {"branch": "Automobile Engineering", "session": "2009-10", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/BTech-AUTO-ENGG-July05-2011-1-old.pdf"},
        {"branch": "Automobile Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech-auto-syll.pdf"},
        {"branch": "Automobile Engineering", "session": "2017-18 and 2018-19 III Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/Syllabus-AE.pdf"},
        {"branch": "Automobile Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/Syllabus-Automobile-Engg..pdf"},
        {"branch": "Automobile Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/AE.pdf"},
        {"branch": "Bio Medical Engineering", "session": "2009-10", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/BTech_Biomedical_Instrumentation_syllabus_subject_to_approva-old.pdf"},
        {"branch": "Bio Medical Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech_Biomedical_Instrumentation_syllabus_subject_to_approva.pdf"},
        {"branch": "Bio Technology", "session": "2009-10", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/BTech_biotech_22-8-09.pdf"},
        {"branch": "Bio Technology", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech_biotech_22-8-09.pdf"},
        {"branch": "Ceramic Engineering", "session": "2009-10", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/BTech_CERAMIC_ENGG_III_and_VIII_Semester.pdf"},
        {"branch": "Ceramic Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech-Ceramic-Syllabus.pdf"},
        {"branch": "Ceramic Engineering", "session": "2017-18 and 2018-19 III Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/Syllabus_Ceramic_III-Sem._RTU.pdf"},
        {"branch": "Ceramic Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/Syllabus-Ceramic-Engg..pdf"},
        {"branch": "Ceramic Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/cr-v-vi.pdf"},
        {"branch": "Chemical Engineering", "session": "2009-10", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/BTech_Chemical-old.pdf"},
        {"branch": "Chemical Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech_Chemical.pdf"},
        {"branch": "Chemical Engineering", "session": "2017-18 and 2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/Syllabus-Chemical-Engg..pdf"},
        {"branch": "Chemical Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/Syllabus-Chemical-Engg..pdf"},
        {"branch": "Chemical Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/CH.pdf"},
        {"branch": "Civil Engineering", "session": "2009-10", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/BTech-Civil-Scheme-and-Syllabi-subject-to-approval-of-Academ.pdf"},
        {"branch": "Civil Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech_Civil_syllabi_12-13.pdf"},
        {"branch": "Civil Engineering", "session": "2017-18 and 2018-19 III Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/3rd-Semester-Syllabus.pdf"},
        {"branch": "Civil Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/Syallabus-Civil-Engg..pdf"},
        {"branch": "Civil Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/08/Civil-v-VI.pdf"},
        {"branch": "Computer Engineering", "session": "2009-10 III-IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/DetailedSyllabus_CS_2009-10_Main-III_IV.pdf"},
        {"branch": "Computer Engineering", "session": "2009-10 V-VIII Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/DetailedSyllabus_CS_2009-10_Main-V-To-VIII.pdf"},
        {"branch": "Computer Engineering", "session": "2010-11 V-VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/Detailed_Syllabus_CS_V_VI_10_11_2.pdf"},
        {"branch": "Computer Engineering", "session": "2011-12 VII-VIII Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/Syllabi_CS_VII___VIII_w.e.f._2011-12.pdf"},
        {"branch": "Computer Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/10/CS_3_8_syllabus 07102015.pdf"},
        {"branch": "Computer Engineering", "session": "2017-18 and 2018-19 III Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/Syllabus-CS.pdf"},
        {"branch": "Computer Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/Syllabus-CS.pdf"},
        {"branch": "Computer Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/CS.pdf"},
        {"branch": "Electrical Engineering", "session": "2011-12", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/EE-B-Tech-Scheme-Syllabus-7july2011-1.pdf"},
        {"branch": "Electrical Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech_Syllabus-EE-3-8-Sem.pdf"},
        {"branch": "Electrical Engineering", "session": "2017-18 and 2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/EE-III-Syll.pdf"},
        {"branch": "Electrical Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/Syllabus-EE.pdf"},
        {"branch": "Electrical Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/EE.pdf"},
        {"branch": "Electrical and Electronics Engineering", "session": "2011-12", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/EEE-B-Tech-Scheme-Syllabus-7july2011_new-1.pdf"},
        {"branch": "Electrical and Electronics Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech_Syllabus-EEE-3-8-Sem.pdf"},
        {"branch": "Electrical and Electronics Engineering", "session": "2017-18 and 2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/Syllabus-EEE-III.pdf"},
        {"branch": "Electrical and Electronics Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/12/Syllabus-EEE-IV.pdf"},
        {"branch": "Electrical and Electronics Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/EX.pdf"},
        {"branch": "Electronic Instrumentation & Control Engineering", "session": "2011-12", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/home_B.Tech-ElC2011-12.pdf"},
        {"branch": "Electronic Instrumentation & Control Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech_EIC_syllabus.pdf"},
        {"branch": "Electronic Instrumentation & Control Engineering", "session": "2017-18 and 2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/3-sem-Syllabus-of-EIC-3.pdf"},
        {"branch": "Electronic Instrumentation & Control Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/Syllabus-EIC.pdf"},
        {"branch": "Electronic Instrumentation & Control Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/EI-v-vi.pdf"},
        {"branch": "Electronics and Communication Engineering", "session": "2011-12", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/home_B.Tech-ECE2011-12.pdf"},
        {"branch": "Electronics and Communication Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech_ECE_syll.pdf"},
        {"branch": "Electronics and Communication Engineering", "session": "2017-18 and 2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/3-Sem-Syllabus-of-EC-2.pdf"},
        {"branch": "Electronics and Communication Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/Syllabus-EC.pdf"},
        {"branch": "Electronics and Communication Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/EC-v-vi.pdf"},
        {"branch": "Food Technology", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech_FT.pdf"},
        {"branch": "Industrial Engineering", "session": "2009-10", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/Syllabus-and-Scheme-BTech-Industrial-Engineering-and-Managem.pdf"},
        {"branch": "Industrial Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/Syllabus-and-Scheme-BTech-Industrial-Engineering-and-Managem.pdf"},
        {"branch": "Information Technology", "session": "2008-09 III-VIII Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/syllabus-and-scheme-of-IT-subject-to-approval-o.pdf"},
        {"branch": "Information Technology", "session": "2009-10 V-VIII Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/DetailedSyllabus_IT_2009-10_Main-V-To-VIII.pdf"},
        {"branch": "Information Technology", "session": "2009-10 III-VIII Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/Syllabi_IT_5_JULY_2011.pdf"},
        {"branch": "Information Technology", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/10/BTech_IT_3_8_syllabus 07102015.pdf"},
        {"branch": "Information Technology", "session": "2017-18 and 2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/Syllabus-IT.pdf"},
        {"branch": "Information Technology", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/Syllabus-IT.pdf"},
        {"branch": "Information Technology", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/IT.pdf"},
        {"branch": "Mechanical Engineering", "session": "2011-12", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/BTech-MECHANICALJuly05-2011.pdf"},
        {"branch": "Mechanical Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech-Mech-Syllabus12_13.pdf"},
        {"branch": "Mechanical Engineering", "session": "2017-18 and 2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/Syllabus-ME.pdf"},
        {"branch": "Mechanical Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/Syllabus-ME.pdf"},
        {"branch": "Mechanical Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/10/me.pdf"},
        {"branch": "Mechanical Engineering", "session": "2019-20 V & VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2020/10/ME-V-VII-semester-syllabus.pdf"},
        {"branch": "Mechatronic Engineering", "session": "B.Tech II Year", "link": "https://rtu.ac.in/home/wp-content/uploads/2016/11/3rd-4th-Semester-of-Mechatronics-Syllabus.pdf"},
        {"branch": "Mechatronic Engineering", "session": "B.Tech III (V-VI) Year", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/10/Final-V-Sem-ME.pdf"},
        {"branch": "Mechatronic Engineering", "session": "2014-15 & Onwards VII & VIII Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/07/Mechatronics-Syllabus-VII-VIII-Sem..pdf"},
        {"branch": "Mechatronic Engineering", "session": "2017-18 and 2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/Mechatronics__III___IV_Sem_Syllabus_2018-19.pdf"},
        {"branch": "Mechatronic Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/Mechatronics__IV_Sem_Syllabus_2018-19.pdf"},
        {"branch": "Mechatronic Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/MH.pdf"},
        {"branch": "Mining Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/RTU_Mining_Syllbi-planwise.pdf"},
        {"branch": "Mining Engineering", "session": "2017-18 and 2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/Syllabus_Mining.pdf"},
        {"branch": "Mining Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/Syllabus_Mining_IV-sem-RTU.pdf"},
        {"branch": "Mining Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/MI-V-VI.pdf"},
        {"branch": "Petrochemical Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech-petrochemical-3_6-syll.pdf"},
        {"branch": "Petrochemical Engineering", "session": "VII & VIII Semester", "link": "https://rtu.ac.in/home/wp-content/uploads/2016/07/Syllabus-of-VII-VIII-Sem-Petrochemical-Engineering.pdf"},
        {"branch": "Petroleum Engineering", "session": "2011-12", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/petro_corrected_upload_on-15.10.2012.pdf"},
        {"branch": "Petroleum Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech-Petroleum-3_8-Syllabus.pdf"},
        {"branch": "Petroleum Engineering", "session": "2017-18 and 2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/PE-Syllabus.pdf"},
        {"branch": "Petroleum Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/PE-syllabus.pdf"},
        {"branch": "Petroleum Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/PE-V_VI.pdf"},
        {"branch": "Production and Industrial Engineering", "session": "2011-12", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/BTech-PI-July05-2011.pdf"},
        {"branch": "Production and Industrial Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech_PI_syll_12_13_.pdf"},
        {"branch": "Production and Industrial Engineering", "session": "2017-18 and 2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/PC-Syllabus.pdf"},
        {"branch": "Production and Industrial Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/PC-Syllabus.pdf"},
        {"branch": "Production and Industrial Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/PC.pdf"},
        {"branch": "Professional Ethics and Disaster Management", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/dm_pe_final.pdf"},
        {"branch": "Textile Chemistry", "session": "2009-10", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/BTechTextile-Chemistry-scheme-and-syllabi-subject-to-approva.pdf"},
        {"branch": "Textile Chemistry", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech-TC-syllabus.pdf"},
        {"branch": "Textile Chemistry", "session": "2017-18 and 2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/BTech_Textile_Chemistry_syllabus_18-19.pdf"},
        {"branch": "Textile Chemistry", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/BTech_Textile_Chemistry_syllabus_18-19.pdf"},
        {"branch": "Textile Chemistry", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/TC.pdf"},
        {"branch": "Textile Engineering", "session": "2008-10", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/BTech_TE_Syllabus_08-09.pdf"},
        {"branch": "Textile Engineering", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech-Textile-Engg-syllabus.pdf"},
        {"branch": "Textile Engineering", "session": "2017-18 and 2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/BTech_Textile_Engg_syllabus_18-19.pdf"},
        {"branch": "Textile Engineering", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/BTech_Textile_Engg_syllabus_18-19.pdf"},
        {"branch": "Textile Engineering", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/TE.pdf"},
        {"branch": "Textile Technology", "session": "2009-10", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/06/Syllabus_and_Scheme_BTech_Textile_Tech_subject_to_approval_of_Academic_Council.pdf"},
        {"branch": "Textile Technology", "session": "2012-13", "link": "https://rtu.ac.in/home/wp-content/uploads/2015/05/BTech-Textile-Tech-syllabus.pdf"},
        {"branch": "Textile Technology", "session": "2017-18 and 2018-19", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/09/BTech_Textile_Tech_syllabus_18-19_.pdf"},
        {"branch": "Textile Technology", "session": "Current and 2018-19 IV Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2018/11/BTech_Textile_Tech_syllabus_18-19_.pdf"},
        {"branch": "Textile Technology", "session": "2019-20 V to VI Sem", "link": "https://rtu.ac.in/home/wp-content/uploads/2019/07/TT.pdf"}
    ]

    # Group data by branch
    branches = {}
    for item in syllabus_data:
        branch = item["branch"]
        if branch not in branches:
            branches[branch] = []
        branches[branch].append({"session": item["session"], "link": item["link"], "id": str(uuid.uuid4())})

    # Define branch order as per provided list
    branch_order = [
        "B.Tech First Year",
        "B.Tech First Year (Revised)",
        "Old First Year Annual Scheme",
        "Aeronautical Engineering",
        "Agricultural Engineering",
        "Applied Electronics & Instrumentation",
        "Automobile Engineering",
        "Bio Medical Engineering",
        "Bio Technology",
        "Ceramic Engineering",
        "Chemical Engineering",
        "Civil Engineering",
        "Computer Engineering",
        "Electrical Engineering",
        "Electrical and Electronics Engineering",
        "Electronic Instrumentation & Control Engineering",
        "Electronics and Communication Engineering",
        "Food Technology",
        "Industrial Engineering",
        "Information Technology",
        "Mechanical Engineering",
        "Mechatronic Engineering",
        "Mining Engineering",
        "Petrochemical Engineering",
        "Petroleum Engineering",
        "Production and Industrial Engineering",
        "Professional Ethics and Disaster Management",
        "Textile Chemistry",
        "Textile Engineering",
        "Textile Technology"
    ]

    # Verify all 30 branches
    if set(branch_order) != set(branches.keys()):
        missing = set(branch_order) - set(branches.keys())
        if missing:
            print(f"Warning: Missing branches: {missing}")

    # Define branch-specific Material Icons
    branch_icons = {
        "B.Tech First Year": "school",
        "B.Tech First Year (Revised)": "school",
        "Old First Year Annual Scheme": "school",
        "Aeronautical Engineering": "flight",
        "Agricultural Engineering": "agriculture",
        "Applied Electronics & Instrumentation": "settings_input_component",
        "Automobile Engineering": "directions_car",
        "Bio Medical Engineering": "medical_services",
        "Bio Technology": "biotech",
        "Ceramic Engineering": "brush",
        "Chemical Engineering": "science",
        "Civil Engineering": "construction",
        "Computer Engineering": "computer",
        "Electrical Engineering": "electrical_services",
        "Electrical and Electronics Engineering": "bolt",
        "Electronic Instrumentation & Control Engineering": "tune",
        "Electronics and Communication Engineering": "router",
        "Food Technology": "kitchen",
        "Industrial Engineering": "factory",
        "Information Technology": "laptop",
        "Mechanical Engineering": "build",
        "Mechatronic Engineering": "precision_manufacturing",
        "Mining Engineering": "landscape",
        "Petrochemical Engineering": "local_gas_station",
        "Petroleum Engineering": "oil_barrel",
        "Production and Industrial Engineering": "settings",
        "Professional Ethics and Disaster Management": "security",
        "Textile Chemistry": "color_lens",
        "Textile Engineering": "book",
        "Textile Technology": "curtains"
    }

    # Generate HTML for cards and modals
    cards_html = ""
    modals_html = ""
    colors = [
        "#FF6F61", "#6B5B95", "#88B04B", "#F7CAC9", "#92A8D1",
        "#955251", "#B565A7", "#009B77", "#DD4124", "#45B8AC",
        "#EFC050", "#5B5EA6", "#9B59B6", "#3498DB", "#E74C3C",
        "#2ECC71", "#F1C40F", "#1ABC9C", "#C0392B", "#2980B9",
        "#8E44AD", "#27AE60", "#D35400", "#7F8C8D", "#E67E22", "#2C3E50",
        "#16A085", "#8B008B", "#FF4500", "#4682B4"
    ]
    cache_bust = str(int(time.time()))

    for idx, branch in enumerate(branch_order):
        if branch not in branches:
            continue
        color = colors[idx % len(colors)]
        icon = branch_icons.get(branch, "menu_book")
        branch_modal_id = f"modal-branch-{idx}"
        cards_html += f"""
        <div class="col-6 col-sm-4 col-md-3 col-lg-2">
          <div class="card tool-card" data-bs-toggle="modal" data-bs-target="#{branch_modal_id}">
            <div class="card-body d-flex flex-column align-items-center justify-content-center">
              <i class="material-icons tool-icon" style="color: {color}; font-size: 40px;">{icon}</i>
              <h6 class="card-title">{branch}</h6>
            </div>
          </div>
        </div>
        """
        # Session list modal with icon bullets
        session_list_html = ""
        for session in branches.get(branch, []):
            session_list_html += f"""
              <li style="padding-left: 25px; position: relative;">
                <i class="material-icons session-icon" style="position: absolute; left: 0; top: 50%; transform: translateY(-50%); font-size: 16px; color: {color};">{icon}</i>
                <h3 style="font-weight: bold; margin: 10px 0; color: #000; font-size: 20px;">
                  <a href="#" class="session-link" data-session-id="{session['id']}" data-pdf-url="{session['link']}" data-branch="{branch}" data-session="{session['session']}" data-color="{color}" data-icon="{icon}">{session['session']}</a>
                </h3>
              </li>
            """
        modals_html += f"""
        <div class="modal fade" id="{branch_modal_id}" tabindex="-1" aria-labelledby="{branch_modal_id}-label">
          <div class="modal-dialog modal-full">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="{branch_modal_id}-label">{branch} - Sessions</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body session-list">
                <ul class="list-unstyled">{session_list_html}</ul>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
              </div>
            </div>
          </div>
        </div>
        """
        # PDF modal with heartbeat loading indicator and error message
        for session in branches.get(branch, []):
            pdf_url = f"{session['link']}?v={cache_bust}"
            modals_html += f"""
            <div class="modal fade" id="pdf-modal-{session['id']}" tabindex="-1" aria-labelledby="pdf-modal-{session['id']}-label">
              <div class="modal-dialog modal-full">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title" id="pdf-modal-{session['id']}-label">{branch} - {session['session']}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                  </div>
                  <div class="modal-body" style="position: relative;">
                    <div class="loading-spinner" style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
                      <i class="material-icons heartbeat" style="font-size: 48px; color: {color}; border-radius: 50%;">{icon}</i>
                      <h2 style="font-weight: bold; margin-top: 10px;">Loading...</h2>
                      <h5 style="font-weight: bold; font-size: 12px;">Please wait while the PDF loads</h5>

                    </div>
                    <div class="error-message" style="display: none; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
                      <i class="material-icons" style="font-size: 48px; color: #E74C3C;">error</i>

                      <h2 style="font-weight: bold; margin-top: 10px; font-size: 12px;">Unable to load session</h2>
                      <h3 style="font-weight: bold; font-size: 12px;">Please try again</h3>
                      <div style="margin-top: 20px;">
                        <button type="button" class="btn btn-primary try-again" data-pdf-url="{session['link']}">Try Again</button>
                      </div>
                    </div>
                    <iframe style="width: 100%; height: 100%; border: none; display: none;"></iframe>
                  </div>
                  <div class="modal-footer">
                    <button type="button" class="btn btn-secondary back-to-sessions" data-branch-modal="{branch_modal_id}">Back</button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                  </div>
                </div>
              </div>
            </div>
            """

    # Generate cache-busting query parameter
    cache_bust = str(int(time.time()))

    html_content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <title>RTUdroid Syllabus</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css?v={cache_bust}" rel="stylesheet">
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons|Material+Symbols+Outlined&v={cache_bust}" rel="stylesheet">
  <style>
    body {{ 
      overflow-x: hidden; 
      background-color: #ffffff; 
    }}
    .container {{ 
      max-width: 100%; 
      padding: 0 15px; 
      margin-left: auto; 
      margin-right: auto; 
    }}
    .tool-card {{ 
      width: 100%; 
      min-width: 140px; 
      height: 160px; 
      cursor: pointer; 
      margin: auto; 
      border-radius: 10px;
      background-color: #ffffff;
      margin-bottom: 10px;
    }}
    .tool-icon {{ 
      font-size: 40px; 
      margin-bottom: 10px; 
    }}
    .card {{ 
      box-shadow: 0 4px 12px rgba(0,0,0,0.3); 
      transition: transform 0.3s, box-shadow 0.3s; 
    }}
    .card:hover {{ 
      transform: translateY(-5px); 
      box-shadow: 0 8px 20px rgba(0,0,0,0.4); 
    }}
    .card-title {{ 
      font-size: 0.9rem; 
      font-weight: 600; 
      text-align: center; 
    }}
    .row {{ 
      display: flex; 
      flex-wrap: wrap; 
      justify-content: space-between; 
      gap: 10px; 
      margin: 0 -15px; 
    }}
    .modal-full {{ 
      max-width: 100%; 
      margin: 0; 
      width: 100vw;
    }}
    .modal-full .modal-content {{ 
      height: 100vh; 
      border-radius: 0; 
      display: flex;
      flex-direction: column;
    }}
    .modal-header {{
      flex-shrink: 0;
      padding: 10px 15px;
    }}
    .modal-title {{
      font-size: 1rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: calc(100% - 40px);
    }}
    .modal-body {{ 
      padding: 0; 
      flex-grow: 1; 
      overflow-y: auto; 
      overflow-x: hidden;
      position: relative;
    }}
    .modal-footer {{ 
      flex-shrink: 0;
      justify-content: center; 
      padding: 10px;
    }}
    .session-list ul {{ 
      font-size: 0.9rem; 
      margin-left: 20px; 
      padding: 20px; 
    }}
    .session-list li {{ 
      margin: 10px 0; 
      position: relative; 
    }}
    .session-icon {{ 
      font-size: 16px; 
      vertical-align: middle; 
    }}
    .session-link {{ 
      color: #000; 
      text-decoration: none; 
    }}
    .session-link:hover {{ 
      color: #007bff; 
      text-decoration: none; 
    }}
    .loading-spinner, .error-message {{ 
      position: absolute; 
      top: 50%; 
      left: 50%; 
      transform: translate(-50%, -50%); 
    }}
    .heartbeat {{ 
      animation: heartbeat 1.5s ease-in-out infinite; 
      border-radius: 50%; 
      padding: 10px; 
      background-color: rgba(0, 0, 0, 0.1); 
    }}
    @keyframes heartbeat {{
      0% {{ transform: scale(1); }}
      20% {{ transform: scale(1.3); }}
      40% {{ transform: scale(1); }}
      60% {{ transform: scale(1.3); }}
      80% {{ transform: scale(1); }}
      100% {{ transform: scale(1); }}
    }}
    .modal-body iframe {{
      width: 100%;
      height: 100%;
      border: none;
    }}
    @media (max-width: 576px) {{
      .col-6 {{ 
        flex: 0 0 calc(50% - 10px); 
        max-width: calc(50% - 10px); 
      }}
      .tool-card {{ 
        min-width: 140px; 
        height: 140px; 
      }}
      .card-title {{ 
        font-size: 0.85rem; 
      }}
      .tool-icon {{ 
        font-size: 35px; 
      }}
      .row {{ 
        justify-content: space-between; 
        margin-left: 0; 
        margin-right: 0; 
      }}
      .container {{ 
        padding-left: 10px; 
        padding-right: 10px; 
      }}
      .modal-title {{
        font-size: 0.9rem;
      }}
    }}
    @media (min-width: 577px) and (max-width: 767px) {{
      .col-sm-4 {{ 
        flex: 0 0 calc(33.333% - 10px); 
        max-width: calc(33.333% - 10px); 
      }}
    }}
    @media (min-width: 768px) {{
      .col-md-3 {{ 
        padding: 0 15px 10px; 
      }}
    }}
    /* Prevent background scrolling when modal is open */
    body.modal-open {{
      overflow: hidden;
      position: fixed;
      width: 100%;
      height: 100%;
    }}
    .modal-backdrop {{
      background-color: rgba(0,0,0,0.5) !important;
    }}
    /* Improve accessibility for hidden modals */
    .modal:not(.show) {{
      display: none !important;
    }}
  </style>
</head>
<body>
  <div class="container mt-4">
    <h2 class="text-center mb-4">RTUdroid Syllabus</h2>
    <div class="row gy-3">
      {cards_html}
    </div>
  </div>

  {modals_html}

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js?v={cache_bust}"></script>
  <script>
    // Ensure Material Icons and Symbols load
    document.querySelectorAll('.material-icons').forEach(icon => {{
      icon.style.fontFamily = "'Material Icons', 'Material Symbols Outlined'";
      icon.style.fontWeight = 'normal';
      icon.style.fontStyle = 'normal';
    }});

    // Handle session link clicks to show PDF modal
    document.querySelectorAll('.session-link').forEach(link => {{
      link.addEventListener('click', function(e) {{
        e.preventDefault();
        const sessionId = this.getAttribute('data-session-id');
        const pdfUrl = this.getAttribute('data-pdf-url');
        const branchModalId = this.closest('.modal').id;

        // Hide current modal
        const currentModal = this.closest('.modal');
        const bootstrapCurrentModal = bootstrap.Modal.getInstance(currentModal);
        bootstrapCurrentModal.hide();

        // Show PDF modal
        const pdfModal = document.getElementById(`pdf-modal-${{sessionId}}`);
        const pdfModalInstance = new bootstrap.Modal(pdfModal);
        pdfModalInstance.show();

        // Move focus to the PDF modal's title
        const modalTitle = pdfModal.querySelector('.modal-title');
        modalTitle.focus();

        // Initialize modal elements
        const iframe = pdfModal.querySelector('iframe');
        const spinner = pdfModal.querySelector('.loading-spinner');
        const errorMessage = pdfModal.querySelector('.error-message');
        let isLoaded = false;
        let timeoutId;

        iframe.style.display = 'none'; // Hide iframe initially
        spinner.style.display = 'flex'; // Show spinner
        errorMessage.style.display = 'none'; // Hide error message

        // Function to load PDF
        function loadPdf() {{
          console.log(`Loading PDF: ${{pdfUrl}}`);
          iframe.src = pdfUrl + '?v=' + new Date().getTime();
          iframe.addEventListener('load', () => {{
            console.log(`Iframe loaded for URL: ${{iframe.src}}`);
            isLoaded = true;
            clearTimeout(timeoutId);
            spinner.style.display = 'none';
            iframe.style.display = 'block';
            errorMessage.style.display = 'none';
          }}, {{ once: true }});
        }}

        // Check PDF validity
        fetch('/check-pdf?url=' + encodeURIComponent(pdfUrl))
          .then(response => response.json())
          .then(data => {{
            console.log(`Checking PDF: ${{pdfUrl}}, Result:`, data);
            if (data.valid) {{
              loadPdf();
            }} else {{
              console.log(`PDF invalid: ${{data.reason}}`);
              spinner.style.display = 'none';
              iframe.style.display = 'none';
              errorMessage.style.display = 'flex';
            }}
          }})
          .catch(error => {{
            console.error('Error checking PDF:', error);
            spinner.style.display = 'none';
            iframe.style.display = 'none';
            errorMessage.style.display = 'flex';
          }});

        // Timeout after 15 seconds
        timeoutId = setTimeout(() => {{
          if (!isLoaded) {{
            console.log(`Timeout triggered for URL: ${{pdfUrl}}`);
            spinner.style.display = 'none';
            iframe.style.display = 'none';
            errorMessage.style.display = 'flex';
          }}
        }}, 15000);

        // Handle try-again button
        pdfModal.querySelector('.try-again').addEventListener('click', () => {{
          console.log(`Try again clicked for URL: ${{pdfUrl}}`);
          isLoaded = false;
          spinner.style.display = 'flex';
          iframe.style.display = 'none';
          errorMessage.style.display = 'none';
          fetch('/check-pdf?url=' + encodeURIComponent(pdfUrl + '?v=' + new Date().getTime()))
            .then(response => response.json())
            .then(data => {{
              console.log(`Retry checking PDF: ${{pdfUrl}}, Result:`, data);
              if (data.valid) {{
                loadPdf();
              }} else {{
                console.log(`PDF invalid on retry: ${{data.reason}}`);
                spinner.style.display = 'none';
                iframe.style.display = 'none';
                errorMessage.style.display = 'flex';
              }}
            }})
            .catch(error => {{
              console.error('Error retrying PDF:', error);
              spinner.style.display = 'none';
              iframe.style.display = 'none';
              errorMessage.style.display = 'flex';
            }});
          timeoutId = setTimeout(() => {{
            if (!isLoaded) {{
              console.log(`Timeout triggered for URL: ${{pdfUrl}}`);
              spinner.style.display = 'none';
              iframe.style.display = 'none';
              errorMessage.style.display = 'flex';
            }}
          }}, 15000);
        }});

        // Handle back button
        pdfModal.querySelector('.back-to-sessions').addEventListener('click', () => {{
          pdfModalInstance.hide();
          const branchModal = document.getElementById(branchModalId);
          const branchModalInstance = new bootstrap.Modal(branchModal);
          branchModalInstance.show();
          const branchModalTitle = branchModal.querySelector('.modal-title');
          branchModalTitle.focus();
        }});
      }});
    }});

    // Prevent touch scrolling on body when modal is open
    document.addEventListener('touchmove', (e) => {{
      if (document.body.classList.contains('modal-open')) {{
        const modal = document.querySelector('.modal.show');
        if (modal && !modal.contains(e.target)) {{
          e.preventDefault();
        }}
      }}
    }}, {{ passive: false }});

    // Manage focus for accessibility
    document.querySelectorAll('.modal').forEach(modal => {{
      modal.addEventListener('shown.bs.modal', () => {{
        const modalTitle = modal.querySelector('.modal-title');
        if (modalTitle) {{
          modalTitle.focus();
        }}
      }});
      modal.addEventListener('hidden.bs.modal', () => {{
        const visibleModal = document.querySelector('.modal.show');
        if (!visibleModal) {{
          const firstCard = document.querySelector('.tool-card');
          if (firstCard) {{
            firstCard.focus();
          }}
        }}
      }});
    }});
  </script>
</body>
</html>"""

    # Set cache-control headers to prevent caching
    response = Response(html_content)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/check-pdf')
def check_pdf():
    url = request.args.get('url')
    if not url:
        return jsonify({"valid": False, "reason": "No URL provided"})
    
    # Check if URL ends with .pdf
    if not url.lower().endswith('.pdf'):
        return jsonify({"valid": False, "reason": "URL does not point to a PDF"})
    
    try:
        # Send HEAD request to check if the resource exists
        response = requests.head(url, timeout=5, allow_redirects=True)
        
        # Check if the response is successful and content type is PDF
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' in content_type:
                return jsonify({"valid": True})
            else:
                # Also check for common PDF content types
                if response.headers.get('content-disposition', '').lower().endswith('.pdf'):
                    return jsonify({"valid": True})
                return jsonify({"valid": False, "reason": "URL does not return a PDF"})
        else:
            # Try with GET request if HEAD is not allowed
            if response.status_code == 405:
                response = requests.get(url, timeout=5, stream=True)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'pdf' in content_type:
                        return jsonify({"valid": True})
                    else:
                        return jsonify({"valid": False, "reason": "URL does not return a PDF"})
                else:
                    return jsonify({"valid": False, "reason": f"HTTP Status: {response.status_code}"})
            else:
                return jsonify({"valid": False, "reason": f"HTTP Status: {response.status_code}"})
    except requests.exceptions.RequestException as e:
        return jsonify({"valid": False, "reason": str(e)})

if __name__ == "__main__":
    app.run(debug=True)