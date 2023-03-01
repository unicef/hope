import { IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { CriteriaAutocomplete } from './TargetingCriteria/CriteriaAutocomplete';

const FlexWrapper = styled.div`
  display: flex;
  justify-content: space-between;
`;

export function FieldChooser({
  onChange,
  fieldName,
  onDelete,
  index,
  choices,
  baseName,
  showDelete,
}: {
  index: number;
  choices;
  fieldName: string;
  onChange: (e, object) => void;
  onDelete: () => void;
  baseName: string;
  showDelete: boolean;
}): React.ReactElement {
  const { t } = useTranslation();
  return (
    <FlexWrapper>
      <Field
        name={`${baseName}.fieldName`}
        label={t('Select Field')}
        required
        choices={choices}
        index={index}
        value={fieldName || null}
        onChange={onChange}
        component={CriteriaAutocomplete}
        data-cy={`field-chooser-${baseName}`}
      />
      {showDelete && (
        <IconButton onClick={onDelete}>
          <Delete />
        </IconButton>
      )}
    </FlexWrapper>
  );
}
