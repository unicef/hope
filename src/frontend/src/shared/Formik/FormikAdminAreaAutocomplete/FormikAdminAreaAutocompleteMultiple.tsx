import { AdminAreaAutocompleteMultiple } from '../../autocompletes/AdminAreaAutocompleteMultiple';
import { FieldLabel } from '@core/FieldLabel';
import { Box } from '@mui/material';
import { t } from 'i18next';
import { ReactElement } from 'react';

export function FormikAdminAreaAutocompleteMultiple({
  field,
  form,
  disabled,
  ...props
}): ReactElement {
  const handleChange = (e, option): void => {
    if (!option) {
      form.setFieldValue(field.name, null);
    } else {
      form.setFieldValue(field.name, option);
    }
  };
  return (
    <Box display="flex" flexDirection="column">
      <FieldLabel>{t('Administrative Level 2')}</FieldLabel>
      <AdminAreaAutocompleteMultiple
        disabled={disabled}
        value={field.value}
        onChange={handleChange}
        {...props}
      />
    </Box>
  );
}
