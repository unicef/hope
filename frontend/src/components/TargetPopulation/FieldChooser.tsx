import React from 'react';
import styled from 'styled-components';
import { Field } from 'formik';
import { IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import { CriteriaAutocomplete } from './TargetingCriteria/CriteriaAutocomplete';

const FlexWrapper = styled.div`
  display: flex;
  justify-content: space-between;
`;

export function FieldChooser({
  onChange,
  fieldName,
  onClick,
  index,
  choices,
  baseName,
  showDelete,
}: {
  index: number;
  choices;
  fieldName: string;
  onChange: (e, object) => void;
  onClick: () => void;
  baseName: string;
  showDelete: boolean;
}): React.ReactElement {
  return (
    <FlexWrapper>
      <Field
        name={`${baseName}.fieldName`}
        label='Choose field type'
        required
        choices={choices}
        index={index}
        value={fieldName || null}
        onChange={onChange}
        component={CriteriaAutocomplete}
      />
      {showDelete && (
        <IconButton onClick={onClick}>
          <Delete />
        </IconButton>
      )}
    </FlexWrapper>
  );
}
