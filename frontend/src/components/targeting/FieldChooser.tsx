import { Box, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { Field } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { CriteriaAutocomplete } from './TargetingCriteria/CriteriaAutocomplete';

export const FieldChooser = ({
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
}): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <Box mb={2} display="flex" justifyContent="space-between">
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
    </Box>
  );
};
