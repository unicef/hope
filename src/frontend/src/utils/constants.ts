import {
  TargetPopulationStatus,
  ProgramStatus,
  PaymentPlanStatus,
  PaymentPlanBackgroundActionStatus,
} from '@generated/graphql';

export const TARGETING_STATES = {
  NONE: 'None',
  [TargetPopulationStatus.Open]: 'Open',
  [TargetPopulationStatus.Locked]: 'Locked',
  [TargetPopulationStatus.ReadyForCashAssist]: 'Ready For Cash Assist',
  [TargetPopulationStatus.ReadyForPaymentModule]: 'Ready For Payment Module',
  [TargetPopulationStatus.Processing]: 'Processing',
  [TargetPopulationStatus.SteficonWait]: 'Entitlement Formula Wait',
  [TargetPopulationStatus.SteficonRun]: 'Entitlement Formula Run',
  [TargetPopulationStatus.SteficonCompleted]: 'Entitlement Formula Completed',
  [TargetPopulationStatus.SteficonError]: 'Entitlement Formula Error',
  [TargetPopulationStatus.Assigned]: 'Assigned',
  [TargetPopulationStatus.SendingToCashAssist]: 'Sending To Cash Assist',
};

export const PROGRAM_STATES = {
  [ProgramStatus.Active]: 'Active',
  [ProgramStatus.Draft]: 'Draft',
  [ProgramStatus.Finished]: 'Finished',
};

export const PAYMENT_PLAN_STATES = {
  [PaymentPlanStatus.Open]: 'Open',
  [PaymentPlanStatus.Locked]: 'Locked',
  [PaymentPlanStatus.LockedFsp]: 'FSP Locked',
  [PaymentPlanStatus.InApproval]: 'In Approval',
  [PaymentPlanStatus.InAuthorization]: 'In Authorization',
  [PaymentPlanStatus.InReview]: 'In Review',
  [PaymentPlanStatus.Accepted]: 'Accepted',
  [PaymentPlanStatus.Finished]: 'Finished',
};

export const PAYMENT_PLAN_BACKGROUND_ACTION_STATES = {
  [PaymentPlanBackgroundActionStatus.RuleEngineRun]: 'Entitlement Formula Run',
  [PaymentPlanBackgroundActionStatus.RuleEngineError]:
    'Entitlement Formula Error',
  [PaymentPlanBackgroundActionStatus.XlsxExporting]: 'XLSX Exporting',
  [PaymentPlanBackgroundActionStatus.XlsxExportError]: 'XLSX Export Error',
  [PaymentPlanBackgroundActionStatus.XlsxImportingEntitlements]:
    'XLSX Importing Entitlements',
  [PaymentPlanBackgroundActionStatus.XlsxImportingReconciliation]:
    'XLSX Importing Reconciliation',
  [PaymentPlanBackgroundActionStatus.XlsxImportError]: 'XLSX Import Error',
};

export const PAYMENT_PLAN_ACTIONS = {
  LOCK: 'LOCK',
  UNLOCK: 'UNLOCK',
  SEND_FOR_APPROVAL: 'SEND_FOR_APPROVAL',
  APPROVE: 'APPROVE',
  AUTHORIZE: 'AUTHORIZE',
  REVIEW: 'REVIEW',
  REJECT: 'REJECT',
};

export const GRIEVANCE_TICKET_STATES = {
  NEW: 1,
  ASSIGNED: 2,
  IN_PROGRESS: 3,
  ON_HOLD: 4,
  FOR_APPROVAL: 5,
  CLOSED: 6,
};

export const GRIEVANCE_CATEGORIES = {
  PAYMENT_VERIFICATION: '1',
  DATA_CHANGE: '2',
  SENSITIVE_GRIEVANCE: '3',
  GRIEVANCE_COMPLAINT: '4',
  NEGATIVE_FEEDBACK: '5',
  REFERRAL: '6',
  POSITIVE_FEEDBACK: '7',
  NEEDS_ADJUDICATION: '8',
  SYSTEM_FLAGGING: '9',
};

export const GRIEVANCE_CATEGORIES_NAMES = {
  1: 'PAYMENT_VERIFICATION',
  2: 'DATA_CHANGE',
  3: 'SENSITIVE_GRIEVANCE',
  4: 'GRIEVANCE_COMPLAINT',
  5: 'NEGATIVE_FEEDBACK',
  6: 'REFERRAL',
  7: 'POSITIVE_FEEDBACK',
  8: 'NEEDS_ADJUDICATION',
  9: 'SYSTEM_FLAGGING',
};

export const GRIEVANCE_ISSUE_TYPES = {
  DATA_BREACH: '1',
  BRIBERY_CORRUPTION_KICKBACKS: '2',
  FRAUD_FORGERY: '3',
  FRAUD_MISUSE: '4',
  HARASSMENT: '5',
  INAPPROPRIATE_STAFF_CONDUCT: '6',
  UNAUTHORIZED_USE: '7',
  CONFLICT_OF_INTEREST: '8',
  GROSS_MISMANAGEMENT: '9',
  PERSONAL_DISPUTES: '10',
  SEXUAL_HARASSMENT: '11',
  MISCELLANEOUS: '12',
  EDIT_HOUSEHOLD: '13',
  EDIT_INDIVIDUAL: '14',
  DELETE_INDIVIDUAL: '15',
  ADD_INDIVIDUAL: '16',
  DELETE_HOUSEHOLD: '17',
  PAYMENT_COMPLAINT: '18',
  FSP_COMPLAINT: '19',
  REGISTRATION_COMPLAINT: '20',
  OTHER_COMPLAINT: '21',
  PARTNER_COMPLAINT: '22',
  UNIQUE_IDENTIFIERS_SIMILARITY: '23',
  BIOGRAPHICAL_DATA_SIMILARITY: '24',
  BIOMETRICS_SIMILARITY: '25',
};

export const GRIEVANCE_ISSUE_TYPES_NAMES = {
  1: 'DATA_BREACH',
  2: 'BRIBERY_CORRUPTION_KICKBACKS',
  3: 'FRAUD_FORGERY',
  4: 'FRAUD_MISUSE',
  5: 'HARASSMENT',
  6: 'INAPPROPRIATE_STAFF_CONDUCT',
  7: 'UNAUTHORIZED_USE',
  8: 'CONFLICT_OF_INTEREST',
  9: 'GROSS_MISMANAGEMENT',
  10: 'PERSONAL_DISPUTES',
  11: 'SEXUAL_HARASSMENT',
  12: 'MISCELLANEOUS',
  13: 'EDIT_HOUSEHOLD',
  14: 'EDIT_INDIVIDUAL',
  15: 'DELETE_INDIVIDUAL',
  16: 'ADD_INDIVIDUAL',
  17: 'DELETE_HOUSEHOLD',
  18: 'PAYMENT_COMPLAINT',
  19: 'FSP_COMPLAINT',
  20: 'REGISTRATION_COMPLAINT',
  21: 'OTHER_COMPLAINT',
  22: 'PARTNER_COMPLAINT',
  23: 'UNIQUE_IDENTIFIERS_SIMILARITY',
  24: 'BIOGRAPHICAL_DATA_SIMILARITY',
  25: 'BIOMETRICS_SIMILARITY',
};

export const GRIEVANCE_CATEGORY_DESCRIPTIONS = {
  DATA_CHANGE:
    'A grievance that is submitted to change in the households or beneficiary status',
  GRIEVANCE_COMPLAINT:
    'A grievance submitted to express dissatisfaction made about an individual, UNICEF/NGO/Partner/Vendor, about a received service or about the process itself',
  REFERRAL:
    'A grievance submitted to direct the reporting individual to another service provider/actor to provide support/help that is beyond the scope of work of UNICEF',
  SENSITIVE_GRIEVANCE:
    'A grievance that shall be treated with sensitivity or which individual wishes to submit anonymously',
  NEEDS_ADJUDICATION:
    'This is a ticket created for individual records suspected of being potential duplicates. Such a ticket requires a review to decide the appropriate action, either to flag the individuals as non-duplicates or to label the record as a duplicate.',
  PAYMENT_VERIFICATION:
    'This refers to a system-generated ticket that is created due to a discrepancy between the amount delivered to the beneficiary (as outlined in the reconciliation report) and the actual amount received by the beneficiary (as reported during the payment verification process).',
  SYSTEM_FLAGGING:
    'This ticket type is generated by the system for an individual who potentially matches an individual on the UN sanction list.',
};

export const GRIEVANCE_ISSUE_TYPE_DESCRIPTIONS = {
  ADD_INDIVIDUAL:
    'A grievance submitted to specifically change in the households to add an individual',
  EDIT_HOUSEHOLD:
    'A grievance submitted to change in the household data (Address, number of individuals, etc.)',
  EDIT_INDIVIDUAL:
    'A grievance submitted to change in the household’s individuals data (Family name, full name, birth date, etc.)',
  DELETE_INDIVIDUAL:
    'A grievance submitted to remove an individual from within a household',
  DELETE_HOUSEHOLD: 'A grievance submitted to remove a household',
  PAYMENT_COMPLAINT: 'A grievance submitted to complain about payments',
  FSP_COMPLAINT:
    'A grievance to report dissatisfaction on service provided by a Financial Service Providers',
  REGISTRATION_COMPLAINT:
    'A grievance submitted on issues/difficulties encountered during the registration of beneficiaries',
  PARTNER_COMPLAINT:
    'A grievance submitted on issues encountered by an implementing partner',
  OTHER_COMPLAINT:
    'Other complaints that do not fall into specific predefined categories',
  DATA_BREACH:
    'Grievance on unauthorized access or disclosure of beneficiary data',
  BRIBERY_CORRUPTION_KICKBACKS:
    'Grievance on illicit payments or favors in exchange for personal gain',
  FRAUD_FORGERY:
    'Grievance related to identity theft or impersonation to benefit from someone’s entitlements',
  FRAUD_MISUSE:
    'Grievance on forgery actions undertaken by third parties’ individuals',
  HARASSMENT:
    'Grievance related to intimidation, mistreatment, or abuse by those in authority',
  INAPPROPRIATE_STAFF_CONDUCT:
    'Grievance related to improper behavior or actions (physical or verbal) by program staff',
  UNAUTHORIZED_USE:
    'Grievance on improper or unauthorized handling or disposal of assets/funds',
  CONFLICT_OF_INTEREST:
    'Grievance on deception or falsification for personal gain',
  GROSS_MISMANAGEMENT:
    'Grievance on mismanagement leading to significant negative impact',
  PERSONAL_DISPUTES:
    'Grievance on conflicts or disagreements between individuals',
  SEXUAL_HARASSMENT:
    'Grievance on unwanted advances, abuse, or exploitation of a sexual nature',
  MISCELLANEOUS: 'Other issues not falling into specific predefined categories',
  //TODO: Add descriptions for the new issue types
};

export const REPORT_TYPES = {
  INDIVIDUALS: '1',
  HOUSEHOLD_DEMOGRAPHICS: '2',
  CASH_PLAN_VERIFICATION: '3',
  PAYMENTS: '4',
  PAYMENT_VERIFICATION: '5',
  CASH_PLAN: '6',
  PROGRAM: '7',
  INDIVIDUALS_AND_PAYMENT: '8',
};

export const REPORTING_STATES = {
  PROCESSING: 1,
  GENERATED: 2,
  FAILED: 3,
};

export const COLLECT_TYPES_MAPPING = {
  A_: 'Unknown',
  A_0: 'None',
  A_1: 'Full',
  A_2: 'Partial',
};
export const GRIEVANCE_TICKETS_TYPES = {
  userGenerated: 0,
  systemGenerated: 1,
};

export const GrievanceTypes = {
  0: 'user',
  1: 'system',
};

export const GrievanceStatuses = {
  All: 'all',
  Active: 'active',
  Closed: 'Closed',
};

export const GrievanceSteps = {
  Selection: 0,
  Lookup: 1,
  Verification: 2,
  Description: 3,
};

export const FeedbackSteps = {
  Selection: 0,
  Lookup: 1,
  Verification: 2,
  Description: 3,
};

export const ISSUE_TYPE_CATEGORIES = {
  DATA_CHANGE: 'Data Change',
  SENSITIVE_GRIEVANCE: 'Sensitive Grievance',
  GRIEVANCE_COMPLAINT: 'Grievance Complaint',
};

export const CommunicationSteps = {
  LookUp: 0,
  SampleSize: 1,
  Details: 2,
};

export const CommunicationTabsValues = {
  HOUSEHOLD: 0,
  TARGET_POPULATION: 1,
  RDI: 2,
};

export const SurveySteps = {
  LookUp: 0,
  SampleSize: 1,
  Details: 2,
};

export const SurveyTabsValues = {
  PROGRAM: 0,
  TARGET_POPULATION: 1,
  RDI: 2,
  A_: 'Unknown',
  A_0: 'None',
  A_1: 'Full',
  A_2: 'Partial',
};

export const householdTableOrderOptions = [
  { name: 'Household Id: ascending', value: 'unicef_id' },
  { name: 'Household Id: descending', value: '-unicef_id' },
  { name: 'Status: ascending', value: 'status_label' },
  { name: 'Status: descending', value: '-status_label' },
  { name: 'Household Size: ascending', value: 'size' },
  { name: 'Household Size: descending', value: '-size' },
  { name: 'Registration Date: ascending', value: 'last_registration_date' },
  { name: 'Registration Date: descending', value: '-last_registration_date' },
];

export const individualTableOrderOptions = [
  { name: 'Individual Id: ascending', value: 'unicef_id' },
  { name: 'Individual Id: descending', value: '-unicef_id' },
  { name: 'Individual: ascending', value: 'full_name' },
  { name: 'Individual: descending', value: '-full_name' },
  { name: 'Gender: ascending', value: 'sex' },
  { name: 'Gender: descending', value: '-sex' },
];
