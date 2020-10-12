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
  arrayHelpers,
  value,
  deleteCondition,
}): React.ReactElement => {
  const FlexWrapper = styled.div`
    display: flex;
    justify-content: space-between;
  `;
  const chooseFieldType = (object, arrHelpers, idx): void => {
    const values = {
      isFlexField: object.isFlexField,
      associatedWith: object.associatedWith,
      fieldAttribute: {
        labelEn: object.labelEn,
        type: object.type,
        choices: null,
      },
      value: null,
    };
    switch (object.type) {
      case 'INTEGER':
        values.value = { from: '', to: '' };
        break;
      case 'SELECT_ONE':
        values.fieldAttribute.choices = object.choices;
        break;
      case 'SELECT_MANY':
        values.value = [];
        values.fieldAttribute.choices = object.choices;
        break;
      default:
        values.value = null;
        break;
    }
    arrHelpers.replace(idx, {
      ...values,
      fieldName: object.name,
      type: object.type,
    });
  };

  const clearField = (arrHelpers, idx): void => {
    return arrHelpers.replace(idx, {});
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
      {deleteCondition && (
        <IconButton>
          <Delete onClick={() => arrayHelpers.remove(index)} />
        </IconButton>
      )}
    </FlexWrapper>
  );
};
