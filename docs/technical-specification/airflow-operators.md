# Airflow Operators

Quick list / description of [Airflow](https://airflow.apache.org/) operators that would be needed.

* RegistrationXLSXImportOperator - Works on valid XLSX files, parsing them and creating households/individuals in the Registration Datahub. Once finished it will update the status of that registration data import instance. 
* RegistrationKoboImportOperator - Imports project data from Kobo via a REST API, parsing them and creating households/individuals in the Registration Datahub. Once finished it will update the status of that registration data import instance.

* RegistrationDataPullOperator - This is when the user merges to population an approved registration data import. This will copy the data over \(taking care of parsing etc.\) from registration datahub to the HCT database \(golden record\). Once finished it will update the status of that registration data import instance \(to 'merged'\). 
* TargetPopulationCAPushOperator - This will take a finalized target population and push to CA datahub the households/individuals and any other relevant data necessary. 
* ProgramCAPushOperator - This will push approved programs \(Programmes\) from HCT database to CA datahub. 
* CashPlanPullOperator - This will pull both \(new & completed\) cash plans + all their associated payment records from the CA datahub to HCT database.



