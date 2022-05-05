export const chooseFieldType = (value, arrayHelpers, index): void => {
  const values = {
    isFlexField: value.isFlexField,
    associatedWith: value.associatedWith,
    fieldAttribute: {
      labelEn: value.labelEn,
      type: value.type,
      choices: null,
    },
    value: null,
  };
  switch (value.type) {
    case 'INTEGER':
      values.value = { from: '', to: '' };
      break;
    case 'DATE':
      values.value = { from: undefined, to: undefined };
      break;
    case 'SELECT_ONE':
      values.fieldAttribute.choices = value.choices;
      break;
    case 'SELECT_MANY':
      values.value = [];
      values.fieldAttribute.choices = value.choices;
      break;
    default:
      values.value = null;
      break;
  }
  arrayHelpers.replace(index, {
    ...values,
    fieldName: value.name,
    type: value.type,
  });
};
export const clearField = (arrayHelpers, index): void => {
  return arrayHelpers.replace(index, {});
};
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function mapFiltersToInitialValues(filters): any[] {
  const mappedFilters = [];
  if (filters) {
    filters.map((each) => {
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
      ),
    })),
  };
}

// TODO Marącin make Type to this function
// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function formatCriteriaFilters(filters) {
  return filters.map((each) => {
    let comparisionMethod;
    let values;
    switch (each.fieldAttribute.type) {
      case 'SELECT_ONE':
        comparisionMethod = 'EQUALS';
        values = [each.value];
        break;
      case 'SELECT_MANY':
        comparisionMethod = 'CONTAINS';
        values = [...each.value];
        break;
      case 'STRING':
        comparisionMethod = 'CONTAINS';
        values = [each.value];
        break;
      case 'DECIMAL':
      case 'INTEGER':
      case 'DATE':
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
      case 'BOOL':
        comparisionMethod = 'EQUALS';
        values = [each.value];
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
export function formatCriteriaIndividualsFiltersBlocks(
  individualsFiltersBlocks,
) {
  return individualsFiltersBlocks.map((block) => ({
    individualBlockFilters: formatCriteriaFilters(block.individualBlockFilters),
  }));
}

function mapFilterToVariable(
  filter,
): {
  comparisionMethod: string;
  arguments;
  fieldName: string;
  isFlexField: boolean;
} {
  return {
    comparisionMethod: filter.comparisionMethod,
    arguments: filter.arguments,
    fieldName: filter.fieldName,
    isFlexField: filter.isFlexField,
  };
}

// TODO Marcin make Type to this function
// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function getTargetingCriteriaVariables(values) {
  return {
    targetingCriteria: {
      rules: values.criterias.map((rule) => {
        return {
          filters: rule.filters.map(mapFilterToVariable),
          individualsFiltersBlocks: rule.individualsFiltersBlocks.map(
            (block) => ({
              individualBlockFilters: block.individualBlockFilters.map(
                mapFilterToVariable,
              ),
            }),
          ),
        };
      }),
    },
  };
}
