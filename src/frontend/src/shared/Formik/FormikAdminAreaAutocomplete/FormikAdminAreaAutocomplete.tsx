import { Box } from '@mui/material';
import { FieldLabel } from '@components/core/FieldLabel';
import { AdminAreaFixedAutocomplete } from '../../autocompletes/AdminAreaFixedAutocomplete';
import { ReactElement } from 'react';

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
}): ReactElement {
  const { label } = props;
  const handleChange = (_, option): void => {
    if (!option) {
      form.setFieldValue(field.name, null);
    } else {
      form.setFieldValue(field.name, option.id);
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
