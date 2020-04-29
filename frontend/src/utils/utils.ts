import moment from 'moment';
import { theme as themeObj } from '../theme';
import {
  AllProgramsQuery,
  ChoiceObject,
  ProgramStatus,
} from '../__generated__/graphql';

const Gender = new Map([
  ['MALE', 'Male'],
  ['FEMALE', 'Female'],
]);

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

export function programStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'ACTIVE':
      return theme.hctPalette.green;
    case 'FINISHED':
      return theme.hctPalette.gray;
    default:
      return theme.hctPalette.oragne;
  }
}

export function cashPlanStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'STARTED':
      return theme.hctPalette.green;
    case 'COMPLETE':
      return theme.hctPalette.gray;
    default:
      return theme.hctPalette.oragne;
  }
}
export function paymentRecordStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'SUCCESS':
      return theme.hctPalette.green;
    case 'PENDING':
      return theme.hctPalette.oragne;
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
      return theme.hctPalette.oragne;
    default:
      return theme.hctPalette.oragne;
  }
}

export function targetPopulationStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'DRAFT':
      return theme.hctPalette.gray;
    case 'APPROVED':
      return theme.hctPalette.oragne;
    case 'FINALIZED':
      return theme.hctPalette.green;
    default:
      return theme.palette.error.main;
  }
}

export function isAuthenticated(): boolean {
  return Boolean(localStorage.getItem('AUTHENTICATED'));
}
export function setAuthenticated(authenticated: boolean): void {
  localStorage.setItem('AUTHENTICATED', `${authenticated}`);
}

export function selectFields(
  fullObject,
  keys: string[],
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
): { [key: string]: any } {
  return keys.reduce((acc, current) => {
    acc[current] = fullObject[current];
    return acc;
  }, {});
}

export function camelToUnderscore(key): string {
  return key.replace(/([A-Z])/g, '_$1').toLowerCase();
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

export function choicesToDict(
  choices: ChoiceObject[],
): { [key: string]: string } {
  return choices.reduce((previousValue, currentValue) => {
    const newDict = { ...previousValue };
    newDict[currentValue.value] = currentValue.name;
    return newDict;
  }, {});
}

export function programStatusToPriority(status: ProgramStatus): number {
  switch (status) {
    case ProgramStatus.Draft:
      return 1;
    case ProgramStatus.Active:
      return 2;
    default:
      return 3;
  }
}
export function decodeIdString(idString): string | null {
  if (!idString) {
    return null;
  }
  const decoded = atob(idString);
  return decoded.split(':')[1];
}

export function programCompare(
  a: AllProgramsQuery['allPrograms']['edges'][number],
  b: AllProgramsQuery['allPrograms']['edges'][number],
): number {
  const statusA = programStatusToPriority(a.node.status);
  const statusB = programStatusToPriority(b.node.status);
  return statusA > statusB ? 1 : -1;
}

export function formatCurrency(amount: number): string {
  const amountCleared = amount || 0;
  return `${amountCleared.toLocaleString('en-US', {
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })} USD`;
}

export function getAgeFromDob(date: string): number {
  return moment().diff(moment(date), 'years');
}
// TODO Marcin make Type to this function
// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function formatCriteriaFilters({ filters }) {
  return filters.map((each) => {
    let comparisionMethod;
    let values;
    switch (each.fieldAttribute.type) {
      case 'SELECT_ONE':
        comparisionMethod = 'EQUALS';
        values = [each.value];
        break;
      case 'SELECT_MANY':
        comparisionMethod = 'EQUALS';
        values = [each.value];
        break;
      case 'STRING':
        comparisionMethod = 'CONTAINS';
        values = [each.value];
        break;
      case 'INTEGER':
        if (each.value.from && each.value.to) {
          comparisionMethod = 'RANGE';
          values = [each.value.from, each.value.to];
        } else if (each.value.from && !each.value.to) {
          comparisionMethod = 'GREATER_THAN';
          values = [each.value.from];
        } else {
          comparisionMethod = 'LESS_THAN';
          values = [each.value.to];
        }
        break;
      default:
        comparisionMethod = 'CONTAINS';
    }
    return {
      comparisionMethod,
      arguments: values,
      fieldName: each.fieldName,
      isFlexField: each.isFlexField,
      fieldAttribute: each.fieldAttribute,
    };
  });
}

// TODO Marcin make Type to this function
// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function mapCriteriasToInitialValues(criteria){
  const mappedFilters = [];
  if (criteria.filters) {
    criteria.filters.map((each) => {
      switch (each.comparisionMethod) {
        case 'RANGE':
          return mappedFilters.push({
            ...each,
            value: {
              from: each.arguments[0],
              to: each.arguments[1],
            },
          });
        case 'LESS_THAN':
          return mappedFilters.push({
            ...each,
            value: {
              from: '',
              to: each.arguments[0],
            },
          });
        case 'GREATER_THAN':
          return mappedFilters.push({
            ...each,
            value: {
              from: each.arguments[0],
              to: '',
            },
          });
        case 'EQUALS':
          return mappedFilters.push({
            ...each,
            value: each.arguments[0],
          });
        default:
          return mappedFilters.push({
            ...each,
          });
      }
    });
  } else {
    mappedFilters.push({ fieldName: '' });
  }
  return mappedFilters;
}

export function targetPopulationStatusMapping(status): string {
  switch (status) {
    case 'DRAFT':
      return 'Open';
    case 'APPROVED':
      return 'Closed';
    case 'FINALIZED':
      return 'Sent';
    default:
      return status;
  }
}
