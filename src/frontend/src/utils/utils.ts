export function safeStringify(value) {
  if (typeof value === 'object' && value !== null) {
    try {
      return JSON.stringify(value);
    } catch {
      return '[object Object]';
    }
  }
  return String(value);
}
// Status color for periodic data updates online edits
export function periodicDataUpdatesOnlineEditsStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'NEW':
      return theme.hctPalette.gray;
    case 'READY':
      return theme.hctPalette.orange;
    case 'APPROVED':
      return theme.hctPalette.green;
    case 'MERGED':
      return theme.hctPalette.darkerBlue;
    case 'MERGING':
      return theme.hctPalette.blue;
    case 'CREATING':
      return theme.hctPalette.blue;
    case 'FAILED_MERGE':
      return theme.hctPalette.red;
    case 'FAILED_CREATE':
      return theme.hctPalette.red;
    default:
      return theme.hctPalette.gray;
  }
}
import { HeadCell } from '@core/Table/EnhancedTableHead';
import { Choice } from '@restgenerated/models/Choice';
import { BackgroundActionStatusEnum } from '@restgenerated/models/BackgroundActionStatusEnum';
import { PaymentPlanStatusEnum as PaymentPlanStatus } from '@restgenerated/models/PaymentPlanStatusEnum';
import { ProgramStatusEnum } from '@restgenerated/models/ProgramStatusEnum';
import localForage from 'localforage';
import _ from 'lodash';
import camelCase from 'lodash/camelCase';
import moment from 'moment';
import { useLocation, useNavigate } from 'react-router-dom';
import { theme as themeObj } from '../theme';
import {
  GRIEVANCE_CATEGORIES,
  PAYMENT_PLAN_BACKGROUND_ACTION_STATES,
  PAYMENT_PLAN_STATES,
  PROGRAM_STATES,
  TARGETING_STATES,
} from './constants';

const Gender = new Map([
  ['MALE', 'Male'],
  ['FEMALE', 'Female'],
  ['OTHER', 'Other'],
  ['NOT_COLLECTED', 'Not Collected'],
  ['NOT_ANSWERED', 'Not Answered'],
]);

export function restChoicesToDict(choices: Choice[] | null): {
  [key: string]: string;
} {
  if (!choices || !choices.length) return {};
  return choices.reduce(
    (dict, choice) => {
      dict[choice.value] = choice.name;
      return dict;
    },
    {} as { [key: string]: string },
  );
}

const IdentificationType = new Map([
  ['NA', 'N/A'],
  ['BIRTH_CERTIFICATE', 'Birth Certificate'],
  ['DRIVING_LICENSE', 'Driving License'],
  ['UNHCR_ID_CARD', 'UNHCR ID Card'],
  ['NATIONAL_ID', 'National ID'],
  ['NATIONAL_PASSPORT', 'National Passport'],
]);

export const getIdentificationType = (idType: string): string => {
  if (IdentificationType.has(idType)) {
    return IdentificationType.get(idType);
  }
  return idType;
};
export const sexToCapitalize = (sex: string): string => {
  if (Gender.has(sex)) {
    return Gender.get(sex);
  }
  return sex;
};

export function opacityToHex(opacity: number): string {
  return Math.floor(opacity * 0xff).toString(16);
}

export const isPartnerVisible = (partnerName: string): boolean => {
  if (!partnerName) return false;
  return (
    !partnerName.startsWith('UNICEF Partner for') && partnerName !== 'UNICEF HQ'
  );
};

export function mapPartnerChoicesWithoutUnicef(choices, selectedPartners) {
  return choices
    .filter((partner) => isPartnerVisible(partner.name))
    .map((partner) => ({
      value: partner.value,
      label: partner.name,
      disabled: selectedPartners.some((p) => p.id === partner.value),
    }));
}

export function periodicDataUpdatesStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'Processing':
      return theme.hctPalette.orange;
    case 'Successful':
      return theme.hctPalette.green;
    case 'Failed':
      return theme.hctPalette.red;
    default:
      return theme.hctPalette.gray;
  }
}

export function programStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case ProgramStatusEnum.DRAFT:
      return theme.hctPalette.gray;
    case ProgramStatusEnum.ACTIVE:
      return theme.hctPalette.green;
    case ProgramStatusEnum.FINISHED:
      return theme.hctPalette.gray;
    default:
      return theme.hctPalette.orange;
  }
}

export function maritalStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'SINGLE':
      return theme.hctPalette.green;
    case 'MARRIED':
      return theme.hctPalette.orange;
    case 'WIDOW':
      return theme.hctPalette.gray;
    case 'DIVORCED':
      return theme.hctPalette.gray;
    case 'SEPARATED':
      return theme.hctPalette.gray;
    default:
      return theme.hctPalette.gray;
  }
}

export function populationStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'ACTIVE':
      return theme.hctPalette.green;
    default:
      return theme.hctPalette.gray;
  }
}

export function paymentStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'Pending':
    case 'Sent to Payment Gateway':
    case 'Sent to FSP':
      return theme.hctPalette.orange;
    case 'Distribution Successful':
    case 'Transaction Successful':
      return theme.hctPalette.green;
    case 'Partially Distributed':
      return theme.hctPalette.lightBlue;
    default:
      return theme.palette.error.main;
  }
}

export function paymentStatusDisplayMap(status: string): string {
  switch (status) {
    case 'Pending':
      return 'PENDING';
    case 'Distribution Successful':
    case 'Transaction Successful':
      return 'DELIVERED FULLY';
    case 'Partially Distributed':
      return 'DELIVERED PARTIALLY';
    case 'Not Distributed':
      return 'NOT DELIVERED';
    case 'Force failed':
      return 'FORCE FAILED';
    case 'Manually Cancelled':
      return 'MANUALLY CANCELLED';
    case 'Sent to Payment Gateway':
      return 'SENT TO PAYMENT GATEWAY';
    case 'Sent to FSP':
      return 'SENT TO FSP';
    default:
      return 'UNSUCCESSFUL';
  }
}

export function targetPopulationStatusDisplayMap(status: string): string {
  switch (status) {
    case PaymentPlanStatus.OPEN:
      return 'OPEN';
    case PaymentPlanStatus.LOCKED:
      return 'LOCKED';
    case PaymentPlanStatus.TP_OPEN:
      return 'OPEN';
    case PaymentPlanStatus.DRAFT:
      return 'READY FOR PAYMENT MODULE';
    case PaymentPlanStatus.TP_LOCKED:
      return 'LOCKED';
    case PaymentPlanStatus.PROCESSING:
      return 'PROCESSING';
    case PaymentPlanStatus.STEFICON_WAIT:
      return 'STEFICON WAIT';
    case PaymentPlanStatus.STEFICON_RUN:
      return 'STEFICON RUN';
    case PaymentPlanStatus.STEFICON_ERROR:
      return 'STEFICON ERROR';
    case PaymentPlanStatus.STEFICON_COMPLETED:
      return 'STEFICON COMPLETED';

    //   if other PP statuses ==> ASSIGNED
    default:
      return 'ASSIGNED';
  }
}

export function paymentVerificationStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'ACTIVE':
      return theme.hctPalette.green;
    case 'PENDING':
      return theme.hctPalette.orange;
    case 'FINISHED':
      return theme.hctPalette.gray;
    default:
      return theme.palette.error.main;
  }
}

export function verificationRecordsStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'PENDING':
      return theme.hctPalette.gray;
    case 'RECEIVED':
      return theme.hctPalette.green;
    case 'NOT_RECEIVED':
      return theme.palette.error.main;
    case 'RECEIVED_WITH_ISSUES':
      return theme.hctPalette.orange;
    default:
      return theme.palette.error.main;
  }
}

export function registrationDataImportStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'APPROVED':
      return theme.hctPalette.green;
    case 'MERGED':
      return theme.hctPalette.gray;
    case 'IN_PROGRESS':
      return theme.hctPalette.orange;
    default:
      return theme.hctPalette.orange;
  }
}

export function registrationDataImportDeduplicationEngineStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'PENDING':
      return theme.hctPalette.gray;
    case 'UPLOADED':
      return theme.hctPalette.orange;
    case 'IN_PROGRESS':
      return theme.hctPalette.orange;
    case 'FINISHED':
      return theme.hctPalette.green;
    case 'UPLOAD_ERROR':
    case 'ERROR':
      return theme.palette.error.main;
    default:
      return theme.hctPalette.orange;
  }
}

export const registrationDataImportErasedColor = (): string =>
  themeObj.palette.error.main;

export function paymentPlanStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  const colorsMap = {
    ['ASSIGNED']: theme.hctPalette.gray,
    [PaymentPlanStatus.ACCEPTED]: theme.hctPalette.green,
    [PaymentPlanStatus.DRAFT]: theme.hctPalette.green,
    [PaymentPlanStatus.FINISHED]: theme.hctPalette.gray,
    [PaymentPlanStatus.IN_APPROVAL]: theme.hctPalette.blue,
    [PaymentPlanStatus.IN_AUTHORIZATION]: theme.hctPalette.blue,
    [PaymentPlanStatus.IN_REVIEW]: theme.hctPalette.blue,
    [PaymentPlanStatus.LOCKED]: theme.hctPalette.red,
    [PaymentPlanStatus.LOCKED_FSP]: theme.hctPalette.red,
    [PaymentPlanStatus.OPEN]: theme.hctPalette.gray,
    [PaymentPlanStatus.PREPARING]: theme.hctPalette.blue,
    [PaymentPlanStatus.PROCESSING]: theme.hctPalette.blue,
    [PaymentPlanStatus.STEFICON_COMPLETED]: theme.hctPalette.green,
    [PaymentPlanStatus.STEFICON_ERROR]: theme.palette.error.main,
    [PaymentPlanStatus.STEFICON_RUN]: theme.hctPalette.blue,
    [PaymentPlanStatus.STEFICON_WAIT]: theme.hctPalette.orange,
    [PaymentPlanStatus.TP_LOCKED]: theme.hctPalette.red,
    [PaymentPlanStatus.TP_OPEN]: theme.hctPalette.gray,
  };
  if (status in colorsMap) {
    return colorsMap[status];
  }
  return theme.hctPalette.gray;
}

export function paymentPlanBuildStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  const colorsMap = {
    OK: theme.hctPalette.green,
    FAILED: theme.hctPalette.red,
    BUILDING: theme.hctPalette.orange,
    PENDING: theme.hctPalette.gray,
  };
  if (status in colorsMap) {
    return colorsMap[status];
  }
  return theme.palette.error.main;
}

export function periodicDataUpdateTemplateStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  const colorsMap = {
    NEW: theme.hctPalette.gray,
    EXPORTED: theme.hctPalette.green,
    FAILED: theme.hctPalette.red,
    TO_EXPORT: theme.hctPalette.gray,
    ['NOT_SCHEDULED']: theme.hctPalette.gray,
    ['CANCELED']: theme.hctPalette.gray,
    EXPORTING: theme.hctPalette.orange,
  };
  if (status in colorsMap) {
    return colorsMap[status];
  }
  return theme.palette.error.main;
}

export function periodicDataUpdatesUpdatesStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  const colorsMap = {
    SUCCESSFUL: theme.hctPalette.green,
    FAILED: theme.hctPalette.red,
    PENDING: theme.hctPalette.gray,
    ['NOT_SCHEDULED']: theme.hctPalette.gray,
    ['CANCELED']: theme.hctPalette.gray,
    PROCESSING: theme.hctPalette.orange,
  };
  if (status in colorsMap) {
    return colorsMap[status];
  }
  return theme.palette.error.main;
}

export function paymentPlanBackgroundActionStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  const colorsMap = {
    [BackgroundActionStatusEnum.RULE_ENGINE_RUN]: theme.hctPalette.gray,
    [BackgroundActionStatusEnum.RULE_ENGINE_ERROR]: theme.palette.error.main,
    [BackgroundActionStatusEnum.XLSX_EXPORTING]: theme.hctPalette.gray,
    [BackgroundActionStatusEnum.XLSX_EXPORT_ERROR]: theme.palette.error.main,
    [BackgroundActionStatusEnum.XLSX_IMPORTING_ENTITLEMENTS]:
      theme.hctPalette.gray,
    [BackgroundActionStatusEnum.XLSX_IMPORTING_RECONCILIATION]:
      theme.hctPalette.gray,
    [BackgroundActionStatusEnum.XLSX_IMPORT_ERROR]: theme.palette.error.main,
    [BackgroundActionStatusEnum.SEND_TO_PAYMENT_GATEWAY]: theme.hctPalette.gray,
    [BackgroundActionStatusEnum.SEND_TO_PAYMENT_GATEWAY_ERROR]:
      theme.palette.error.main,
  };
  if (status in colorsMap) {
    return colorsMap[status];
  }
  return theme.palette.error.main;
}

export function userStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'INVITED':
      return theme.hctPalette.gray;
    case 'ACTIVE':
      return theme.hctPalette.green;
    case 'INACTIVE':
      return theme.palette.error.main;
    default:
      return theme.palette.error.main;
  }
}

export function householdStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'ACTIVE':
      return theme.hctPalette.green;
    case 'INACTIVE':
      return theme.palette.error.main;
    default:
      return theme.palette.error.main;
  }
}

export function individualStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'ACTIVE':
      return theme.hctPalette.green;
    case 'INACTIVE':
      return theme.palette.error.main;
    default:
      return theme.palette.error.main;
  }
}

export function grievanceTicketStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'New':
      return theme.hctPalette.orange;
    case 'Assigned':
      return theme.hctPalette.darkerBlue;
    case 'In Progress':
      return theme.hctPalette.green;
    case 'On Hold':
      return theme.palette.error.main;
    case 'For Approval':
      return theme.hctPalette.darkBrown;
    case 'Closed':
      return theme.hctPalette.gray;
    default:
      return theme.palette.error.main;
  }
}

export function grievanceTicketBadgeColors(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'Not urgent':
    case 'Low':
      return theme.hctPalette.green;
    case 'Very urgent':
    case 'High':
      return theme.palette.error.main;
    case 'Urgent':
    case 'Medium':
      return theme.hctPalette.orange;
    default:
      return theme.palette.error.main;
  }
}

export function reportStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'Generated':
      return theme.hctPalette.green;
    case 'Processing':
      return theme.hctPalette.gray;
    default:
      return theme.palette.error.main;
  }
}

export function programCycleStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'Draft':
      return theme.hctPalette.gray;
    case 'Active':
      return theme.hctPalette.green;
    case 'Finished':
      return theme.hctPalette.gray;
    default:
      return theme.hctPalette.gray;
  }
}

export function selectFields(
  fullObject,
  keys: string[],
): { [key: string]: any } {
  return keys.reduce((acc, current) => {
    acc[current] = fullObject[current];
    return acc;
  }, {});
}

export function camelToUnderscore(key): string {
  return key.replace(/([A-Z])/g, '_$1').toLowerCase();
}

export function camelizeArrayObjects(arr: any[]): { [key: string]: any }[] {
  if (!Array.isArray(arr)) {
    return arr;
  }

  return arr.map(camelizeObjectKeys);
}

export function camelizeObjectKeys(obj): { [key: string]: any } {
  if (!obj) {
    return obj;
  }
  return Object.keys(obj).reduce((acc, current) => {
    if (obj[current] == null) {
      acc[camelCase(current)] = obj[current];
    } else if (Array.isArray(obj[current])) {
      acc[camelCase(current)] = camelizeArrayObjects(obj[current]);
    } else if (typeof obj[current] === 'object') {
      acc[camelToUnderscore(current)] = camelizeObjectKeys(obj[current]);
    } else {
      acc[camelCase(current)] = obj[current];
    }
    return acc;
  }, {});
}

export function columnToOrderBy(
  column: string,
  orderDirection: string,
): string {
  if (column.startsWith('-')) {
    const clearColumn = column.replace('-', '');
    return camelToUnderscore(
      `${orderDirection === 'asc' ? '-' : ''}${clearColumn}`,
    );
  }
  return camelToUnderscore(`${orderDirection === 'desc' ? '-' : ''}${column}`);
}

export function choicesToDict(choices: Array<Record<string, any>>): {
  [key: string]: string;
} {
  if (!choices) return {};
  return choices.reduce((previousValue, currentValue) => {
    const newDict = { ...previousValue };
    newDict[currentValue.value] = currentValue.name;
    return newDict;
  }, {});
}

export function programStatusToPriority(status: string): number {
  switch (status) {
    case ProgramStatusEnum.DRAFT:
      return 1;
    case ProgramStatusEnum.ACTIVE:
      return 2;
    default:
      return 3;
  }
}

function isBase64(str) {
  if (typeof str !== 'string') return false;
  if (!str.length || str.length % 4 !== 0) return false;
  // Regex covers pure base64 (no mime or data: prefix)
  return /^[A-Za-z0-9+/]+={0,2}$/.test(str);
}

export function decodeIdString(idString: string): string | null {
  if (!idString) {
    return null;
  }
  if (!isBase64(idString)) return idString;
  if (idString.includes(':')) {
    // Already decoded
    return idString.split(':')[1];
  }
  // Check for valid base64 (length multiple of 4, only base64 chars)
  const base64Pattern = /^[A-Za-z0-9+/=]+$/;
  if (idString.length % 4 !== 0 || !base64Pattern.test(idString)) {
    console.error('decodeIdString: Not a valid base64 string:', idString);
    return null;
  }
  try {
    const decoded = atob(idString);
    return decoded.split(':')[1];
  } catch (e) {
    console.error('Failed to decode string:', e, idString);
    return null;
  }
}

export function formatCurrency(
  amount: number,
  onlyNumberValue = false,
): string {
  const amountCleared = amount || 0;
  return `${amountCleared.toLocaleString('en-US', {
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}${onlyNumberValue ? '' : ' USD'}`;
}

export function formatCurrencyWithSymbol(
  amount: number | string,
  currency = 'USD',
): string {
  const amountCleared = amount || 0;
  if (currency === 'USDC') return `${amountCleared} ${currency}`;
  // if currency is unknown, simply format using most common formatting option, and don't show currency symbol
  if (!currency) return formatCurrency(Number(amountCleared), true);
  // undefined forces to use local browser settings
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency,
    // enable this if decided that we always want code and not a symbol
    currencyDisplay: 'code',
  }).format(Number(amountCleared));
}

export function countPercentage(
  partialValue: number,
  totalValue: number,
): number {
  if (!totalValue || !partialValue) return 0;
  return +((partialValue / totalValue) * 100).toFixed(2);
}

export function getPercentage(
  partialValue: number,
  totalValue: number,
): string {
  return `${countPercentage(partialValue, totalValue)}%`;
}

export function formatNumber(value: number): string {
  if (!value && value !== 0) return '0';
  return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
}

export function formatThousands(value: string): string {
  if (!value) return value;
  if (parseInt(value, 10) >= 10000) {
    return `${value.toString().slice(0, -3)}k`;
  }
  return value;
}

export function PaymentPlanStatusMapping(status): string {
  return TARGETING_STATES[status];
}

export function programStatusMapping(status): string {
  return PROGRAM_STATES[status];
}

export function paymentPlanStatusMapping(status): string {
  return PAYMENT_PLAN_STATES[status];
}

export function paymentPlanBackgroundActionStatusMapping(status): string {
  return PAYMENT_PLAN_BACKGROUND_ACTION_STATES[status];
}

export function stableSort(array, comparator) {
  const stabilizedThis = array.map((el, index) => [el, index]);
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) return order;
    return a[1] - b[1];
  });
  return stabilizedThis.map((el) => el[0]);
}

export function descendingComparator(a, b, orderBy): number {
  if (b[orderBy] < a[orderBy]) {
    return -1;
  }
  if (b[orderBy] > a[orderBy]) {
    return 1;
  }
  return 0;
}

export function getComparator(
  order,
  orderBy,
): (a: number, b: number) => number {
  return order === 'desc'
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

export function renderUserName(user): string {
  if (!user) {
    return '-';
  }
  return user?.firstName
    ? `${user?.firstName} ${user?.lastName}`
    : `${user?.email}`;
}

export const getPhoneNoLabel = (
  phoneNo: string,
  phoneNoValid?: boolean,
): string => {
  if (!phoneNo) return '-';
  if (phoneNoValid === false) {
    return 'Invalid Phone Number';
  }
  return phoneNo;
};

const grievanceTypeIssueTypeDict: { [id: string]: boolean | string } = {
  [GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK]: false,
  [GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK]: false,
  [GRIEVANCE_CATEGORIES.REFERRAL]: false,
  [GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT]: false,
  [GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE]: true,
  [GRIEVANCE_CATEGORIES.DATA_CHANGE]: true,
};

export function thingForSpecificGrievanceType(
  ticket: { category: number | string; issueType?: number | string },
  thingDict,
  defaultThing = null,
  categoryWithIssueTypeDict = grievanceTypeIssueTypeDict,
) {
  const category = ticket.category?.toString();
  const issueType = ticket.issueType?.toString();
  if (!(category in thingDict)) {
    return defaultThing;
  }
  const categoryThing = thingDict[category];
  if (
    categoryWithIssueTypeDict[category] === 'IGNORE' ||
    (!categoryWithIssueTypeDict[category] &&
      (issueType === null || issueType === undefined))
  ) {
    return categoryThing;
  }
  if (!(issueType in categoryThing)) {
    return defaultThing;
  }
  return categoryThing[issueType];
}

export const isInvalid = (fieldname: string, errors, touched): boolean =>
  errors[fieldname] && touched[fieldname];

export const anon = (inputStr: string, shouldAnonymize: boolean): string => {
  if (!inputStr) return null;
  return shouldAnonymize
    ? inputStr
        .split(' ')
        .map((el) => el.substring(0, 2) + '*'.repeat(3))
        .join(' ')
    : inputStr;
};

export const isPermissionDeniedError = (error): boolean =>
  error?.message.includes('Permission Denied');

export const getFlexFieldTextValue = (_key, value, fieldAttribute): string => {
  let textValue = value;
  if (!fieldAttribute) return textValue;
  if (fieldAttribute.type === 'SELECT_ONE') {
    textValue =
      fieldAttribute.choices.find((item) => item.value === value)?.labelEn ||
      value;
  }
  if (fieldAttribute.type === 'SELECT_MANY') {
    const values = fieldAttribute.choices.filter((item) =>
      value.includes(item.value),
    );
    textValue = values.map((item) => item.labelEn).join(', ');
  }

  return textValue;
};

export function renderSomethingOrDash(something): number | string | boolean {
  if (something === null || something === undefined) {
    return '-';
  }
  return something;
}

export function renderBoolean(booleanValue: boolean): string {
  if (booleanValue === null || booleanValue === undefined) {
    return '-';
  }
  switch (booleanValue) {
    case true:
      return 'Yes';
    default:
      return 'No';
  }
}

export const formatAge = (age): string | number => {
  if (age > 0) {
    return age;
  }
  return '<1';
};

export const renderIndividualName = (individual): string =>
  individual?.fullName;

export async function clearCache(apolloClient = null): Promise<void> {
  if (apolloClient) apolloClient.resetStore();
  localStorage.clear();
  await localForage.clear();
}

export const round = (value: number, decimals = 2): number =>
  Math.round((value + Number.EPSILON) * 10 ** decimals) / 10 ** decimals;

type Location = ReturnType<typeof useLocation>;
type FilterValue = string | string[] | boolean | null | undefined;
type Filter = { [key: string]: FilterValue };

export const getFilterFromQueryParams = (
  location: Location,
  initialFilter: Filter = {},
): Filter => {
  const filter: Filter = { ...initialFilter };

  try {
    const searchParams = new URLSearchParams(location.search);

    for (const [key, value] of searchParams.entries()) {
      if (key in filter) {
        const existingValue = filter[key];

        if (Array.isArray(existingValue)) {
          const values = value.split(',');
          filter[key] = [...existingValue, ...values];
        } else {
          filter[key] =
            value !== 'true' && value !== 'false' ? value : value === 'true';
        }
      }
    }
  } catch (error) {
    console.error('Error parsing query parameters:', error);
    return { ...initialFilter };
  }

  return filter;
};

export const setQueryParam = (
  key: string,
  value: string,
  navigate: ReturnType<typeof useNavigate>,
  location: Location,
): void => {
  const params = new URLSearchParams(location.search);

  // Remove all existing values for the given key
  params.delete(key);

  // Add the new value for the given key
  params.append(key, value);

  navigate({ search: params.toString() });
};

export const setFilterToQueryParams = (
  filter: { [key: string]: FilterValue },
  navigate: ReturnType<typeof useNavigate>,
  location: Location,
): void => {
  const params = new URLSearchParams(location.search);
  Object.entries(filter).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (Array.isArray(value)) {
        // remove all existing params for this key
        params.delete(key);

        // add each value as a separate param
        value.forEach((val) => {
          if (val !== null && val !== undefined) {
            params.append(key, val);
          }
        });
      } else {
        const paramValue =
          typeof value === 'boolean' ? value.toString() : value;
        params.set(key, paramValue);
      }
    } else {
      params.delete(key);
    }
  });
  const search = params.toString();
  navigate({ search });
};

export const createHandleFilterChange = (
  onFilterChange: (filter: { [key: string]: FilterValue }) => void,
  initialFilter: Filter,
  navigate: ReturnType<typeof useNavigate>,
  location: Location,
): ((key: string, value: FilterValue) => void) => {
  let filterFromQueryParams = getFilterFromQueryParams(location, initialFilter);

  const handleFilterChange = (key: string, value: FilterValue): void => {
    const newFilter = {
      ...filterFromQueryParams,
      [key]: value,
    };

    filterFromQueryParams = newFilter;
    onFilterChange(newFilter);

    const params = new URLSearchParams(location.search);
    const isEmpty = (v: FilterValue): boolean =>
      v === '' ||
      v === null ||
      v === undefined ||
      (Array.isArray(v) && v.length === 0);

    if (isEmpty(value)) {
      params.delete(key);
    } else if (Array.isArray(value)) {
      const filteredValues = value.filter((v) => !isEmpty(v));
      if (filteredValues.length > 0) {
        params.set(key, filteredValues.join(','));
      } else {
        params.delete(key);
      }
    } else {
      params.set(key, value.toString());
    }

    const search = params.toString();
    navigate({ search });
  };

  return handleFilterChange;
};

type HandleFilterChange = (key: string, value: FilterValue) => void;
type HandleApplyFilterChanges = () => void;
type HandleClearFilter = () => void;

interface HandleFilterChangeFunctions {
  handleFilterChange: HandleFilterChange;
  applyFilterChanges: HandleApplyFilterChanges;
  clearFilter: HandleClearFilter;
}

export const createHandleApplyFilterChange = (
  initialFilter: Filter,
  navigate: ReturnType<typeof useNavigate>,
  location: Location,
  filter: Filter,
  setFilter: (filter: { [key: string]: FilterValue }) => void,
  appliedFilter: Filter,
  setAppliedFilter: (filter: Filter) => void,
): HandleFilterChangeFunctions => {
  const handleFilterChange = (key: string, value: FilterValue): void => {
    const newFilter = {
      ...filter,
      [key]: value,
    };

    setFilter(newFilter);
  };

  const applyFilterChanges = (): void => {
    setAppliedFilter(filter);

    const params = new URLSearchParams(location.search);
    Object.entries(filter).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value)) {
          params.delete(key);
          value.forEach((val) => {
            if (val !== null && val !== undefined) {
              params.append(key, val);
            }
          });
        } else {
          const paramValue =
            typeof value === 'boolean' ? value.toString() : value;
          params.set(key, paramValue);
        }
      } else {
        params.delete(key);
      }
    });

    const search = params.toString();
    navigate({ search });

    setFilter(filter);
  };

  const clearFilter = (): void => {
    const params = new URLSearchParams(location.search);
    Object.keys(appliedFilter).forEach((key) => {
      params.delete(key);
    });
    const search = params.toString();
    navigate({ search });
    setFilter(initialFilter);
    setAppliedFilter(initialFilter);
  };

  return {
    handleFilterChange,
    applyFilterChanges,
    clearFilter,
  };
};

export const tomorrow = new Date().setDate(new Date().getDate() + 1);
export const today = new Date();
today.setHours(0, 0, 0, 0);

type DateType = 'startOfDay' | 'endOfDay';

export const dateToIsoString = (date: Date, type: DateType): string => {
  if (!date) return null;
  if (type === 'startOfDay') {
    return moment.utc(date).startOf('day').toISOString();
  }
  if (type === 'endOfDay') {
    return moment.utc(date).endOf('day').toISOString();
  }
  throw new Error('Invalid type specified');
};

// autocompletes utils
export const handleAutocompleteChange = (
  name,
  value,
  handleFilterChange,
): void => {
  if (value === null || value === undefined) {
    handleFilterChange(name, '');
  }
  if (value) {
    handleFilterChange(name, value);
  }
};

export const handleAutocompleteClose = (
  setOpen,
  onInputTextChange,
  reason,
): void => {
  setOpen(false);
  if (reason === 'select-option') return;
  onInputTextChange('');
};

export const getAutocompleteOptionLabel = (
  option,
  edges,
  inputValue: string,
  type: 'default' | 'individual' | 'language' = 'default',
): string => {
  const renderNameOrEmail = (node): string => {
    if (!node) {
      return '-';
    }
    if (node?.firstName && node?.lastName) {
      return `${node.firstName} ${node.lastName}`;
    }
    if (node?.email) {
      return `${node.email}`;
    }
    return '-';
  };

  let optionLabel;
  if (option?.node) {
    switch (type) {
      case 'individual':
        optionLabel = renderNameOrEmail(option.node);
        break;
      case 'language':
        optionLabel = `${option.node.english}`;
        break;
      default:
        optionLabel = `${option.node.name}`;
    }
  } else {
    let foundNode;
    switch (type) {
      case 'individual':
        foundNode = edges?.find((el) => el.node?.id === option)?.node;
        optionLabel = foundNode ? renderNameOrEmail(foundNode) : inputValue;
        break;
      case 'language':
        foundNode = edges?.find((el) => el.node?.code === option)?.node;
        optionLabel = foundNode ? `${foundNode.english}` : inputValue;
        break;
      default:
        foundNode = edges?.find((el) => el.node?.id === option)?.node;
        optionLabel = foundNode ? `${foundNode?.name}` : inputValue;
    }
  }
  return optionLabel;
};

export const handleOptionSelected = (
  option: string | undefined,
  value: string | null | undefined,
): boolean => {
  if (!value) {
    return !option;
  }
  return option === value;
};

export const isProgramNodeUuidFormat = (id: string): boolean => {
  const regex =
    /^ProgramNode:[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
  try {
    const base64 = id.replace(/-/g, '+').replace(/_/g, '/');
    const decodedId = atob(base64);
    return regex.test(decodedId);
  } catch {
    return false;
  }
};

export const arraysHaveSameContent = (a: any[], b: any[]): boolean =>
  a.length === b.length && a.every((val, index) => val === b[index]);

export function adjustHeadCells<T>(
  headCells: HeadCell<T>[],
  beneficiaryGroup: any | undefined,
  replacements: {
    [key: string]: (beneficiaryGroup) => string;
  },
) {
  if (!beneficiaryGroup) return headCells;
  return headCells.map((cell) => {
    // @ts-ignore
    if (replacements[cell.id]) {
      // @ts-ignore
      return { ...cell, label: replacements[cell.id](beneficiaryGroup) };
    }
    return cell;
  });
}

export const filterEmptyParams = (params) => {
  if (!params) return {};

  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => {
      // Handle basic empty values
      if (
        value === undefined ||
        value === null ||
        value === '' ||
        (Array.isArray(value) && value.length === 1 && value[0] === '')
      ) {
        return false;
      }

      // Handle empty arrays
      if (Array.isArray(value) && value.length === 0) {
        return false;
      }

      // Handle JSON strings that represent empty objects or objects with empty values
      if (
        typeof value === 'string' &&
        (value.startsWith('{') || value.startsWith('['))
      ) {
        try {
          const parsedValue = JSON.parse(value);

          // Empty arrays in JSON format
          if (Array.isArray(parsedValue) && parsedValue.length === 0) {
            return false;
          }

          // Objects with empty values
          if (typeof parsedValue === 'object' && parsedValue !== null) {
            const hasNonEmptyValue = Object.values(parsedValue).some(
              (v) => v !== '' && v !== null && v !== undefined,
            );
            return hasNonEmptyValue;
          }
        } catch {
          // If parsing fails, keep the value
          return true;
        }
      }

      return true;
    }),
  );
};

export function deepCamelize(data) {
  const notCalizedKeys = ['form_errors', 'household_data'];
  if (_.isArray(data)) {
    return data.map(deepCamelize);
  } else if (_.isObject(data)) {
    return _.reduce(
      data,
      (result, value, key) => {
        const camelKey = _.camelCase(key);
        if (notCalizedKeys.includes(key)) {
          // Special handling for error_info to keep it as is
          result[camelKey] = value;
          return result;
        }
        result[camelKey] = deepCamelize(value);
        return result;
      },
      {},
    );
  }
  return data;
}

export function deepUnderscore(data) {
  if (_.isArray(data)) {
    return data.map(deepUnderscore);
  } else if (_.isObject(data)) {
    return _.reduce(
      data,
      (result, value, key) => {
        // Special handling for keys that follow the pattern of letters followed by numbers
        if (/^[a-zA-Z]+\d+$/.test(key)) {
          // Keep original key for letter+number pattern fields
          result[key] = deepUnderscore(value);
        } else {
          // Normal snake_case conversion for other fields
          const underscoreKey = _.snakeCase(key);
          result[underscoreKey] = deepUnderscore(value);
        }
        return result;
      },
      {},
    );
  }
  return data;
}

export const fieldNameToLabel = (fieldName: string): string => {
  if (!fieldName) return '';

  return fieldName
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

export function showApiErrorMessages(
  error: any,
  showMessage: (msg: string) => void,
  fallbackMsg: string = 'An error occurred',
): void {
  // Helper to convert field names to readable labels and remove array indexes
  function formatFieldLabel(field: string): string {
    let cleaned = field.replace(/\[\d+\]/g, '');
    cleaned = cleaned.split('.').pop();
    let label = cleaned.replace(/_/g, ' ');
    label = label.replace(/([a-z])([A-Z])/g, '$1 $2');
    label = label
      .split(' ')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
    return label.trim();
  }

  // Collect errors per field
  function collectErrors(
    obj: any,
    path: string = '',
    errors: Record<string, string[]> = {},
  ) {
    if (Array.isArray(obj)) {
      obj.forEach((item) => {
        collectErrors(item, path, errors);
      });
    } else if (obj && typeof obj === 'object') {
      Object.entries(obj).forEach(([key, value]) => {
        const newPath = path ? `${path}.${key}` : key;
        collectErrors(value, newPath, errors);
      });
    } else if (typeof obj === 'string') {
      const label = path ? formatFieldLabel(path) : '';
      if (!errors[label]) errors[label] = [];
      errors[label].push(obj);
    }
    return errors;
  }

  const messages: string[] = [];

  // Handle plain array of strings (e.g. ["msg1", "msg2"])
  if (Array.isArray(error) && error.every((item) => typeof item === 'string')) {
    showMessage(error.join('  \n'));
    return;
  }

  // Handle array of errors in error.body
  if (error && typeof error === 'object' && Array.isArray(error.body)) {
    // If error.body is a plain array of strings
    if (error.body.every((item) => typeof item === 'string')) {
      showMessage(error.body.join('  \n'));
      return;
    }
    const errors = collectErrors(error.body);
    Object.entries(errors).forEach(([label, msgs]) => {
      msgs.forEach((msg) => {
        messages.push(`${label}: ${msg}`);
      });
    });
    showMessage(messages.join('  \n'));
    return;
  }
  // Handle string error in error.body
  if (error && typeof error === 'object' && typeof error.body === 'string') {
    showMessage(error.body);
    return;
  }
  // Handle object of arrays/objects in error.body (field errors)
  if (
    error &&
    typeof error === 'object' &&
    typeof error.body === 'object' &&
    error.body !== null
  ) {
    const errors = collectErrors(error.body);
    Object.entries(errors).forEach(([label, msgs]) => {
      msgs.forEach((msg) => {
        messages.push(`${label}: ${msg}`);
      });
    });
    showMessage(messages.join('  \n'));
    return;
  }
  // Handle top-level object of arrays (field errors)
  if (error && typeof error === 'object' && error !== null) {
    const errors = collectErrors(error);
    Object.entries(errors).forEach(([label, msgs]) => {
      msgs.forEach((msg) => {
        messages.push(`${label}: ${msg}`);
      });
    });
    showMessage(messages.join('  \n'));
    return;
  }
  // Handle string error in error.message
  if (error && typeof error === 'object' && typeof error.message === 'string') {
    showMessage(error.message);
    return;
  }
  showMessage(fallbackMsg);
}

export function getApiErrorMessages(
  error: any,
  fallbackMsg: string = 'An error occurred',
): string {
  function formatFieldLabel(field: string): string {
    let cleaned = field.replace(/\[\d+\]/g, '');
    cleaned = cleaned.split('.').pop();
    let label = cleaned.replace(/_/g, ' ');
    label = label.replace(/([a-z])([A-Z])/g, '$1 $2');
    label = label
      .split(' ')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
    return label.trim();
  }

  function collectErrors(
    obj: any,
    path: string = '',
    errors: Record<string, string[]> = {},
  ) {
    if (Array.isArray(obj)) {
      obj.forEach((item) => {
        collectErrors(item, path, errors);
      });
    } else if (obj && typeof obj === 'object') {
      Object.entries(obj).forEach(([key, value]) => {
        const newPath = path ? `${path}.${key}` : key;
        collectErrors(value, newPath, errors);
      });
    } else if (typeof obj === 'string') {
      const label = path ? formatFieldLabel(path) : '';
      if (!errors[label]) errors[label] = [];
      errors[label].push(obj);
    }
    return errors;
  }

  const messages: string[] = [];

  if (Array.isArray(error) && error.every((item) => typeof item === 'string')) {
    return error.join('  \n');
  }

  if (error && typeof error === 'object' && Array.isArray(error.body)) {
    if (error.body.every((item) => typeof item === 'string')) {
      return error.body.join('  \n');
    }
    const errors = collectErrors(error.body);
    Object.entries(errors).forEach(([label, msgs]) => {
      msgs.forEach((msg) => {
        messages.push(`${label}: ${msg}`);
      });
    });
    return messages.join('  \n');
  }
  if (error && typeof error === 'object' && typeof error.body === 'string') {
    return error.body;
  }
  if (
    error &&
    typeof error === 'object' &&
    typeof error.body === 'object' &&
    error.body !== null
  ) {
    const errors = collectErrors(error.body);
    Object.entries(errors).forEach(([label, msgs]) => {
      msgs.forEach((msg) => {
        messages.push(`${label}: ${msg}`);
      });
    });
    return messages.join('  \n');
  }
  if (error && typeof error === 'object' && error !== null) {
    const errors = collectErrors(error);
    Object.entries(errors).forEach(([label, msgs]) => {
      msgs.forEach((msg) => {
        messages.push(`${label}: ${msg}`);
      });
    });
    return messages.join('  \n');
  }
  if (error && typeof error === 'object' && typeof error.message === 'string') {
    return error.message;
  }
  return fallbackMsg;
}

// Utility to split camelCase/PascalCase and capitalize
export function splitCamelCase(str: string): string {
  if (!str) return '';
  // Insert space before all caps, then capitalize first letter
  const withSpaces = str
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (s) => s.toUpperCase());
  return withSpaces.trim();
}
