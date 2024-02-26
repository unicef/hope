import { Box } from '@mui/material';
import * as React from 'react';
import { FieldLabel } from '@components/core/FieldLabel';
import { AdminAreaFixedAutocomplete } from '../../autocompletes/AdminAreaFixedAutocomplete';

export function FormikAdminAreaAutocomplete({
  field,
  form,
  disabled,
  level,
  parentId,
  onClear,
  additionalOnChange,
  dataCy,
  ...props
}): React.ReactElement {
  const { label } = props;
  const handleChange = (_, option): void => {
    console.log('option', option);
    if (!option) {
      form.setFieldValue(field.name, null);
    } else {
      form.setFieldValue(field.name, option.node.id);
    }
  };
  return (
    <Box display="flex" flexDirection="column">
      {label && <FieldLabel>{label}</FieldLabel>}
      <AdminAreaFixedAutocomplete
        disabled={disabled}
        value={field.value}
        onChange={handleChange}
        level={level}
        parentId={parentId}
        onClear={onClear}
        additionalOnChange={additionalOnChange}
        dataCy={dataCy}
        {...props}
      />
    </Box>
  );
}
