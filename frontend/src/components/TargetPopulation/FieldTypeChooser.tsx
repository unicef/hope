import React from 'react';
import styled from 'styled-components';
import { Field } from 'formik';
import { CriteriaAutocomplete } from './TargetingCriteria/CriteriaAutocomplete';
import { IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';

export const FieldTypeChooser = ({
  fieldName,
  index,
  choices,
  each,
  arrayHelpers,
  values,
  value,
  onDeleteCondition,
}): React.ReactElement => {
  const FlexWrapper = styled.div`
    display: flex;
    justify-content: space-between;
  `;

  const chooseFieldType = (fieldValue, helpers, fieldIndex): void => {
    const fieldProperties = {
      isFlexField: fieldValue.isFlexField,
      associatedWith: fieldValue.associatedWith,
      fieldAttribute: {
        labelEn: fieldValue.labelEn,
        type: fieldValue.type,
        choices: null,
      },
      value: null,
    };
    switch (fieldValue.type) {
      case 'INTEGER':
        fieldProperties.value = { from: '', to: '' };
        break;
      case 'SELECT_ONE':
        fieldProperties.fieldAttribute.choices = fieldValue.choices;
        break;
      case 'SELECT_MANY':
        fieldProperties.value = [];
        fieldProperties.fieldAttribute.choices = fieldValue.choices;
        break;
      default:
        fieldProperties.value = null;
        break;
    }
    helpers.replace(fieldIndex, {
      ...fieldProperties,
      fieldName: fieldValue.name,
      type: fieldValue.type,
    });
  };

  const clearField = (helpers, fieldIndex): void => {
    return helpers.replace(fieldIndex, {});
  };

  return (
    <FlexWrapper>
      <Field
        name={fieldName}
        label='Choose field type'
        required
        choices={choices}
        index={index}
        value={value}
        onChange={(e, object) => {
          if (object) {
            return chooseFieldType(object, arrayHelpers, index);
          }
          return clearField(arrayHelpers, index);
        }}
        component={CriteriaAutocomplete}
      />
      {onDeleteCondition && (
        <IconButton>
          <Delete onClick={() => arrayHelpers.remove(index)} />
        </IconButton>
      )}
    </FlexWrapper>
  );
};
