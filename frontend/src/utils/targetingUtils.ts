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

export function mapCriteriasToInitialValues(criteria) {
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
        case 'CONTAINS':
          return mappedFilters.push({
            ...each,
            value: each.arguments,
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
        comparisionMethod = 'CONTAINS';
        values = [...each.value];
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
