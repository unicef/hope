import * as Yup from 'yup';

// validationHelpers.ts

export const filterNullOrNoSelections = (filter): boolean =>
  !filter.isNull &&
  (filter.value === null ||
    filter.value === '' ||
    (filter?.fieldAttribute?.type === 'SELECT_MANY' &&
      filter.value &&
      filter.value.length === 0));

export const filterEmptyFromTo = (filter): boolean =>
  !filter.isNull &&
  typeof filter.value === 'object' &&
  filter.value !== null &&
  Object.prototype.hasOwnProperty.call(filter.value, 'from') &&
  Object.prototype.hasOwnProperty.call(filter.value, 'to') &&
  !filter.value.from &&
  !filter.value.to;

export const validate = (values, beneficiaryGroup) => {
  const hasHouseholdsFiltersBlocksErrors =
    values.householdsFiltersBlocks.some(filterNullOrNoSelections) ||
    values.householdsFiltersBlocks.some(filterEmptyFromTo);

  const hasBlockFiltersErrors = (blocks) => {
    if (!blocks || !Array.isArray(blocks)) {
      return false;
    }

    return blocks.some((block) => {
      if (!block.blockFilters || !Array.isArray(block.blockFilters)) {
        return false;
      }

      const hasNulls = block.blockFilters.some(filterNullOrNoSelections);
      const hasFromToError = block.blockFilters.some(filterEmptyFromTo);
      return hasNulls || hasFromToError;
    });
  };

  const hasIndividualsFiltersBlocksErrors = hasBlockFiltersErrors(
    values.individualsFiltersBlocks,
  );
  const hasCollectorsFiltersBlocksErrors = hasBlockFiltersErrors(
    values.collectorsFiltersBlocks,
  );

  const errors: { nonFieldErrors?: string[] } = {};
  if (
    hasHouseholdsFiltersBlocksErrors ||
    hasIndividualsFiltersBlocksErrors ||
    hasCollectorsFiltersBlocksErrors
  ) {
    errors.nonFieldErrors = ['You need to fill out missing values.'];
  }
  if (
    values.householdsFiltersBlocks.length +
      values.individualsFiltersBlocks.length +
      values.collectorsFiltersBlocks.length ===
      0 &&
    (!values.householdIds || values.householdIds.length === 0) &&
    (!values.individualIds || values.individualIds.length === 0)
  ) {
    errors.nonFieldErrors = [
      `You need to add at least one ${beneficiaryGroup?.groupLabel} filter or an ${beneficiaryGroup?.memberLabel} block filter.`,
    ];
  } else if (
    values.individualsFiltersBlocks.filter(
      (block) => block.blockFilters && block.blockFilters.length === 0,
    ).length > 0 ||
    values.collectorsFiltersBlocks.filter(
      (block) => block.blockFilters && block.blockFilters.length === 0,
    ).length > 0
  ) {
    errors.nonFieldErrors = [
      `You need to add at least one ${beneficiaryGroup?.groupLabel} filter or an ${beneficiaryGroup?.memberLabel} block filter.`,
    ];
  }
  return errors;
};

export const HhIndIdValidation = Yup.string().test(
  'testName',
  'ID is not in the correct format',
  (ids) => {
    if (!ids?.length) {
      return true;
    }
    const idsArr = ids.split(',');
    return idsArr.every((el) => /^\s*(IND|HH)-\d{2}-\d{4}\.\d{4}\s*$/.test(el));
  },
);

export const HhIdValidation = Yup.string().test(
  'testName',
  'Household ID is not in the correct format',
  (ids) => {
    if (!ids?.length) {
      return true;
    }
    const idsArr = ids.split(',');
    return idsArr.every((el) => /^\s*(HH)-\d{2}-\d{4}\.\d{4}\s*$/.test(el));
  },
);

export const IndIdValidation = Yup.string().test(
  'testName',
  'Individual ID is not in the correct format',
  (ids) => {
    if (!ids?.length) {
      return true;
    }
    const idsArr = ids.split(',');
    return idsArr.every((el) => /^\s*(IND)-\d{2}-\d{4}\.\d{4}\s*$/.test(el));
  },
);

export const chooseFieldType = (fieldValue, arrayHelpers, index): void => {
  let flexFieldClassification;
  if (fieldValue.isFlexField === false) {
    flexFieldClassification = 'NOT_FLEX_FIELD';
  } else if (fieldValue.isFlexField === true && fieldValue.type !== 'PDU') {
    flexFieldClassification = 'FLEX_FIELD_BASIC';
  } else if (fieldValue.isFlexField === true && fieldValue.type === 'PDU') {
    flexFieldClassification = 'FLEX_FIELD_PDU';
  }

  const updatedFieldValues = {
    flexFieldClassification,
    associatedWith: fieldValue.associatedWith,
    fieldAttribute: {
      labelEn: fieldValue.labelEn,
      type: fieldValue.type,
      choices: null,
    },
    value: null,
    pduData: fieldValue.pduData,
  };

  switch (fieldValue.type) {
    case 'INTEGER':
      updatedFieldValues.value = { from: '', to: '' };
      break;
    case 'DATE':
      updatedFieldValues.value = { from: undefined, to: undefined };
      break;
    case 'SELECT_ONE':
      updatedFieldValues.fieldAttribute.choices = fieldValue.choices;
      break;
    case 'SELECT_MANY':
      updatedFieldValues.value = [];
      updatedFieldValues.fieldAttribute.choices = fieldValue.choices;
      break;
    default:
      updatedFieldValues.value = null;
      break;
  }

  arrayHelpers.replace(index, {
    ...updatedFieldValues,
    fieldName: fieldValue.name,
    type: fieldValue.type,
  });
};

export const clearField = (arrayHelpers, index): void =>
  arrayHelpers.replace(index, {});

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function mapFiltersToInitialValues(filters): any[] {
  const mappedFilters = [];
  if (filters) {
    filters.map((each) => {
      switch (each.comparisonMethod) {
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
            value:
              each.fieldAttribute?.type === 'BOOL' ||
              each?.type === 'BOOL' ||
              each?.fieldAttribute?.pduData?.subtype === 'BOOL' ||
              each.fieldAttribute?.pduData?.subtype
                ? each.arguments[0]
                  ? 'Yes'
                  : 'No'
                : each.arguments[0],
          });
        case 'CONTAINS':
          // eslint-disable-next-line no-case-declarations
          let value;
          if (each?.fieldAttribute?.type === 'SELECT_MANY') {
            value = each.arguments;
          } else {
            value =
              typeof each.arguments === 'string'
                ? each.arguments
                : each.arguments[0];
          }
          return mappedFilters.push({
            ...each,
            value,
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

function mapBlockFilters(blocks, blockKey) {
  return blocks.map((block) => ({
    [`${blockKey}BlockFilters`]: mapFiltersToInitialValues(
      block[`${blockKey}BlockFilters`],
    ).map((filter) => {
      return {
        ...filter,
        isNull: filter.comparisonMethod === 'IS_NULL' || filter.isNull,
      };
    }),
  }));
}

export function mapCriteriaToInitialValues(criteria) {
  const individualIds = criteria.individualIds || '';
  const householdIds = criteria.householdIds || '';
  const deliveryMechanism = criteria.deliveryMechanism || '';
  const fsp = criteria.fsp || '';
  const householdsFiltersBlocks = criteria.householdsFiltersBlocks || [];
  const individualsFiltersBlocks = criteria.individualsFiltersBlocks || [];
  const collectorsFiltersBlocks = criteria.collectorsFiltersBlocks || [];

  const adjustedCollectorsFiltersBlocks = collectorsFiltersBlocks.map(
    (block) => ({
      ...block,
      collectorBlockFilters: block.collectorBlockFilters.map((filter) => ({
        ...filter,
        arguments: filter.arguments.map((arg) =>
          arg === true ? 'Yes' : arg === false ? 'No' : arg,
        ),
      })),
    }),
  );

  return {
    deliveryMechanism,
    fsp,
    individualIds,
    householdIds,
    householdsFiltersBlocks: mapFiltersToInitialValues(householdsFiltersBlocks),
    individualsFiltersBlocks: mapBlockFilters(
      individualsFiltersBlocks,
      'individual',
    ),
    collectorsFiltersBlocks: mapBlockFilters(
      adjustedCollectorsFiltersBlocks,
      'collector',
    ),
  };
}

// TODO Marącin make Type to this function
// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function formatCriteriaFilters(filters) {
  return filters.map((each) => {
    let comparisonMethod;
    let values;
    switch (each?.fieldAttribute?.type || each?.type) {
      case 'SELECT_ONE':
        comparisonMethod = 'EQUALS';
        values = [each.value];
        break;
      case 'SELECT_MANY':
        comparisonMethod = 'CONTAINS';
        values = [...each.value];
        break;
      case 'STRING':
        comparisonMethod = 'CONTAINS';
        if (
          each.associatedWith === 'Account' ||
          //trick for Collector fields
          each.associatedWith === undefined
        ) {
          comparisonMethod = 'EQUALS';
        }
        values = [each.value];
        break;
      case 'DECIMAL':
      case 'INTEGER':
      case 'DATE':
        if (each.value.from && each.value.to) {
          comparisonMethod = 'RANGE';
          values = [each.value.from, each.value.to];
        } else if (each.value.from && !each.value.to) {
          comparisonMethod = 'GREATER_THAN';
          values = [each.value.from];
        } else {
          comparisonMethod = 'LESS_THAN';
          values = [each.value.to];
        }
        break;
      case 'BOOL':
        comparisonMethod = 'EQUALS';
        values = [each.value];
        break;
      case 'PDU':
        switch (
          each.pduData?.subtype ||
          each.fieldAttribute?.pduData?.subtype
        ) {
          case 'SELECT_ONE':
            comparisonMethod = 'EQUALS';
            values = [each.value];
            break;
          case 'SELECT_MANY':
            comparisonMethod = 'CONTAINS';
            values = [...each.value];
            break;
          case 'STRING':
            comparisonMethod = 'CONTAINS';
            values = [each.value];
            break;
          case 'DECIMAL':
          case 'INTEGER':
          case 'DATE':
            if (each.value.from && each.value.to) {
              comparisonMethod = 'RANGE';
              values = [each.value.from, each.value.to];
            } else if (each.value.from && !each.value.to) {
              comparisonMethod = 'GREATER_THAN';
              values = [each.value.from];
            } else {
              comparisonMethod = 'LESS_THAN';
              values = [each.value.to];
            }
            break;
          case 'BOOL':
            comparisonMethod = 'EQUALS';
            values = [each.value === 'Yes'];
            break;
          default:
            comparisonMethod = 'CONTAINS';
            values = [each.value];
        }
        break;
      default:
        comparisonMethod = 'CONTAINS';
        values = [each.value];
    }

    return {
      ...each,
      comparisonMethod,
      arguments: values,
      fieldName: each.fieldName,
      fieldAttribute: each.fieldAttribute,
      flexFieldClassification: each.flexFieldClassification,
    };
  });
}

// TODO Marcin make Type to this function
// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function formatCriteriaIndividualsFiltersBlocks(
  individualsFiltersBlocks,
) {
  return individualsFiltersBlocks.map((block) => ({
    individualBlockFilters: formatCriteriaFilters(block.individualBlockFilters),
  }));
}

export function formatCriteriaCollectorsFiltersBlocks(collectorsFiltersBlocks) {
  return collectorsFiltersBlocks.map((block) => ({
    collectorBlockFilters: formatCriteriaFilters(block.collectorBlockFilters),
  }));
}

interface Filter {
  isNull: boolean;
  comparisonMethod: string;
  arguments: any[];
  fieldName: string;
  flexFieldClassification: string;
  roundNumber?: number;
  associatedWith: string;
}

interface Result {
  comparisonMethod: string;
  arguments: any[];
  fieldName: string;
  flexFieldClassification: string;
  roundNumber?: number;
}

function mapFilterToVariable(filter: Filter): Result {
  let preparedArguments = [];
  if (filter?.associatedWith === 'Account') {
    preparedArguments = filter.isNull ? [null] : filter.arguments;
  } else {
    preparedArguments = filter.isNull
      ? [null]
      : filter.arguments.map((arg) =>
          arg === 'Yes' ? true : arg === 'No' ? false : arg,
        );
  }
  const result: Result = {
    comparisonMethod: filter.isNull ? 'IS_NULL' : filter.comparisonMethod,
    arguments: preparedArguments,
    fieldName: filter.fieldName,
    flexFieldClassification: filter.flexFieldClassification,
  };

  if (filter.flexFieldClassification === 'FLEX_FIELD_PDU') {
    result.roundNumber = filter.roundNumber;
  }

  return result;
}

// TODO Marcin make Type to this function
// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function getTargetingCriteriaVariables(values) {
  return {
    rules: values.criterias.map((criteria) => ({
      individualIds: criteria.individualIds,
      householdIds: criteria.householdIds,
      householdsFiltersBlocks:
        criteria.householdsFiltersBlocks.map(mapFilterToVariable),
      individualsFiltersBlocks: criteria.individualsFiltersBlocks.map(
        (block) => ({
          individualBlockFilters:
            block.individualBlockFilters.map(mapFilterToVariable),
        }),
      ),
      collectorsFiltersBlocks: criteria.collectorsFiltersBlocks.map(
        (block) => ({
          collectorBlockFilters:
            block.collectorBlockFilters.map(mapFilterToVariable),
        }),
      ),
    })),
  };
}

const flexFieldClassificationMap = {
  NOT_FLEX_FIELD: 'Not a Flex Field',
  FLEX_FIELD_BASIC: 'Flex Field Basic',
  FLEX_FIELD_PDU: 'Flex Field PDU',
};

export function mapFlexFieldClassification(key: string): string {
  return flexFieldClassificationMap[key] || 'Unknown Classification';
}
