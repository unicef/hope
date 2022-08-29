import { TargetPopulationStatus } from '../__generated__/graphql';

export const TARGETING_STATES = {
  NONE: 'None',
  [TargetPopulationStatus.Draft]: 'Open',
  [TargetPopulationStatus.Locked]: 'Locked',
  [TargetPopulationStatus.ReadyForCashAssist]: 'Ready For Cash Assist',
  [TargetPopulationStatus.Processing]: 'Processing',
  [TargetPopulationStatus.SteficonWait]: 'Steficon Wait',
  [TargetPopulationStatus.SteficonRun]: 'Steficon Run',
  [TargetPopulationStatus.SteficonCompleted]: 'Steficon Completed',
  [TargetPopulationStatus.SteficonError]: 'Steficon Error',
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
  DEDUPLICATION: '8',
  SYSTEM_FLAGGING: '9',
};

export const GRIEVANCE_SUB_CATEGORIES = {
  PAYMENT_COMPLAINT: '1',
  FSP_COMPLAINT: '2',
  REGISTRATION_COMPLAINT: '3',
  OTHER_COMPLAINT: '4',
  PARTNER_COMPLAINT: '5',
};

export const GRIEVANCE_ISSUE_TYPES = {
  EDIT_HOUSEHOLD: '13',
  EDIT_INDIVIDUAL: '14',
  DELETE_INDIVIDUAL: '15',
  ADD_INDIVIDUAL: '16',
  DELETE_HOUSEHOLD: '17',
};

export const GRIEVANCE_SUBCATEGORIES = {
  PAYMENT_RELATED_COMPLAINT: '1',
  FSP_RELATED_COMPLAINT: '2',
  REGISTRATION_RELATED_COMPLAINT: '3',
  OTHER_COMPLAINT: '4',
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

export const GrievanceSearchTypes = {
  TicketID: 'ticket_id',
  HouseholdID: 'ticket_hh_id',
  LastName: 'last_name',
};

export const REPORTING_STATES = {
  PROCESSING: 1,
  GENERATED: 2,
  FAILED: 3,
};

export const GrievanceSteps = {
  Selection: 0,
  Lookup: 1,
  Verification: 2,
  Description: 3,
};

export const ISSUE_TYPE_CATEGORIES = {
  DATA_CHANGE: 'Data Change',
  SENSITIVE_GRIEVANCE: 'Sensitive Grievance',
};
