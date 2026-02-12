{
    "name": "HR Hospital",
    "version": "19.0.1.0.0",
    "summary": "Allows to track patients and doctors",
    "author": "Lisa",
    "website": "https://www.lipsum.com/",
    "category": "Human Resources",
    "license": "OPL-1",
    'depends': ['base', ],

    'data': [
        "security/ir.model.access.csv",
        "data/hr_hospital_disease_data.xml",
        "views/hr_hospital_menus.xml",
        "views/hr_hospital_disease_views.xml",
        "views/hr_hospital_contact_person_views.xml",
        "views/hr_hospital_doctor_views.xml",
        "views/hr_hospital_patient_views.xml",
        "views/hr_hospital_diagnosis_views.xml",
        "views/hr_hospital_visit_views.xml",
    ],
    'demo': [
        "demo/hr_hospital_contact_person_demo.xml",
        "demo/hr_hospital_doctor_speciality_demo.xml",
        "demo/hr_hospital_doctor_demo.xml",
        "demo/hr_hospital_patient_demo.xml",
        "demo/hr_hospital_visit_demo.xml",
        "demo/hr_hospital_diagnosis_demo.xml",
        "demo/hr_hospital_doctor_schedule_demo.xml",
        "demo/hr_hospital_patient_doctor_history_demo.xml",
    ],

    'installable': True,
    'auto_install': False,
    'images': ['static/description/icon.png'],

}
