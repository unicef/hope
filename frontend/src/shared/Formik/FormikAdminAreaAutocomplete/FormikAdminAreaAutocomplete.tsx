import { Box } from '@material-ui/core';
import React from 'react';
import { FieldLabel } from '../../../components/core/FieldLabel';
import { AdminAreaFixedAutocomplete } from '../../autocompletes/AdminAreaFixedAutocomplete';

export const FormikAdminAreaAutocomplete = ({
  field,
  form,
  disabled,
  ...props
}): React.ReactElement => {
  const { label } = props;
  const handleChange = (e, option): void => {
    if (!option) {
      form.setFieldValue(field.name, null);
    } else {
      form.setFieldValue(field.name, option);
    }
  };
  return (
    <Box display='flex' flexDirection='column'>
      {label && <FieldLabel>{label}</FieldLabel>}
      <AdminAreaFixedAutocomplete
        disabled={disabled}
        value={field.value}
        onChange={handleChange}
        {...props}
      />
    </Box>
  );
};
