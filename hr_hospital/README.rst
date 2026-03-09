===========
HR Hospital
===========


Comprehensive hospital management system for Odoo 19. This module automates medical facility operations,
from doctor scheduling to patient clinical history tracking.

Key Features
============

* **Medical Staff Management**:
    * Support for Doctors and Interns with a mentorship system.
    * Automatic experience calculation based on license dates.
    * Professional specialty classification.
* **Patient Care**:
    * Electronic Medical Records (EMR) with blood type and allergy tracking.
    * Hierarchical disease classifier (ICD-10 compatible).
    * Automatic logging of attending doctor history.
* **Visit Operations**:
    * Scheduling system with weekend and vacation conflict validation.
    * Support for various visit types: Initial, Return, Preventive, Emergent.
    * Mass reassign and reschedule wizards.
* **Reporting & Data**:
    * Diagnosis reports with Pivot and Graph views.
    * Patient card export to JSON/CSV formats.
    * Automated schedule generation for multiple weeks.

Installation
============

To install this module, you need to:

#. Clone repository.
#. Add the repository path to the config file.
#. Update the app list.
#. Install the module.

Configuration
=============

1. Go to **Settings > Users & Companies > Groups**.
2. Assign users to appropriate roles: **Patient, Intern, Doctor, Manager,** or **Admin**.
3. Configure **Doctor Specialties** in the Hospital menu.

Usage
=====

* **Scheduling**: Use the "Schedule Fill Wizard" to mass-generate doctor shifts.
* **Visits**: Create visits from the Doctor's Kanban view or the Patient's form.
* **Reports**: Access the Reporting menu to generate diagnosis analytics by date and disease.

Credits
=======

Authors
-------
* Lisa

Maintainer
----------
Lisa <lisa@somemail.com>.