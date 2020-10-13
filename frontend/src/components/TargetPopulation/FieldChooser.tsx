import React from 'react';
import styled from 'styled-components';
import { Field } from 'formik';
import { CriteriaAutocomplete } from './TargetingCriteria/CriteriaAutocomplete';
import { IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';

const FlexWrapper = styled.div`
  display: flex;
  justify-content: space-between;
`;

export function FieldChooser({
                               onChange,
                               fieldName,
                               onClick,
                               filters,
                               index,
                               choices,
                             }: {
  index: number;
  choices;
  fieldName: string;
  onChange: (e, object) => void;
  filters;
  onClick: () => void;
}): React.ReactElement {
  return (
      <FlexWrapper>
        <Field
            name={`filters[${index}].fieldName`}
            label='Choose field type'
            required
            choices={choices}
            index={index}
            value={fieldName || null}
            onChange={onChange}
            component={CriteriaAutocomplete}
        />
        {filters.length > 1 && (
            <IconButton onClick={onClick}>
              <Delete />
            </IconButton>
        )}
      </FlexWrapper>
  );
}
