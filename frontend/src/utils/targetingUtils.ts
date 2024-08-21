export const chooseFieldType = (fieldValue, arrayHelpers, index): void => {
  let flexFieldClassification;
  if (fieldValue.isFlexField === false) {
    flexFieldClassification = 'NOT_FLEX_FIELD';
  } else if (fieldValue.isFlexField === true && fieldValue.type !== 'PDU') {
    flexFieldClassification = 'FLEX_FIELD_NOT_PDU';
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
              each.fieldAttribute.type === 'BOOL' ||
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

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function mapCriteriaToInitialValues(criteria) {
  const filters = criteria.filters || [];
  const individualsFiltersBlocks = criteria.individualsFiltersBlocks || [];
  return {
    filters: mapFiltersToInitialValues(filters),
    individualsFiltersBlocks: individualsFiltersBlocks.map((block) => ({
      individualBlockFilters: mapFiltersToInitialValues(
        block.individualBlockFilters,
      ).map((filter) => {
        return {
          ...filter,
          isNull: filter.comparisonMethod === 'IS_NULL',
        };
      }),
    })),
  };
}

// TODO Marącin make Type to this function
// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function formatCriteriaFilters(filters) {
  return filters.map((each) => {
    let comparisonMethod;
    let values;
    switch (each.fieldAttribute.type) {
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
            values = [each.value === 'True'];
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

interface Filter {
  isNull: boolean;
  comparisonMethod: string;
  arguments: any[];
  fieldName: string;
  flexFieldClassification: string;
  roundNumber?: number;
}

interface Result {
  comparisonMethod: string;
  arguments: any[];
  fieldName: string;
  flexFieldClassification: string;
  roundNumber?: number;
}

function mapFilterToVariable(filter: Filter): Result {
  const result: Result = {
    comparisonMethod: filter.isNull ? 'IS_NULL' : filter.comparisonMethod,
    arguments: filter.isNull
      ? [null]
      : filter.arguments.map((arg) =>
          arg === 'True' || arg === 'Yes'
            ? true
            : arg === 'False' || arg === 'No'
              ? false
              : arg,
        ),
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
    targetingCriteria: {
      householdIds: values.householdIds,
      individualIds: values.individualIds,
      flagExcludeIfActiveAdjudicationTicket:
        values.flagExcludeIfActiveAdjudicationTicket,
      flagExcludeIfOnSanctionList: values.flagExcludeIfOnSanctionList,
      rules: values.criterias.map((rule) => ({
        filters: rule.filters.map(mapFilterToVariable),
        individualsFiltersBlocks: rule.individualsFiltersBlocks.map(
          (block) => ({
            individualBlockFilters:
              block.individualBlockFilters.map(mapFilterToVariable),
          }),
        ),
      })),
    },
  };
}

const flexFieldClassificationMap = {
  NOT_FLEX_FIELD: 'Not a Flex Field',
  FLEX_FIELD_NOT_PDU: 'Flex Field Not PDU',
  FLEX_FIELD_PDU: 'Flex Field PDU',
};

export function mapFlexFieldClassification(key: string): string {
  return flexFieldClassificationMap[key] || 'Unknown Classification';
}
