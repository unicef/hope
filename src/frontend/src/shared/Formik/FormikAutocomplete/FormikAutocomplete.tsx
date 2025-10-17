import { Autocomplete, Box, TextField } from '@mui/material';
import { ReactElement } from 'react';

export function FormikAutocomplete({
  field,
  form,
  choices,
  label,
  required = false,
}): ReactElement {
  const realSelectedValue = choices.find((item) => item.value === field.value);

  const handleChange = (e, option): void => {
    if (!option) {
      form.setFieldValue(field.name, null);
    } else {
      form.setFieldValue(field.name, option.value);
    }
  };

  const showError = Boolean(
    form.touched[field.name] && form.errors[field.name],
  );
  const helperText = showError ? form.errors[field.name] : '';

  return (
    <Box mt={2}>
      <Autocomplete
        id="combo-box-demo"
        size="small"
        options={choices}
        onChange={handleChange}
        value={realSelectedValue}
        getOptionLabel={(choice) => choice.labelEn}
        renderInput={(params) => (
          <TextField
            {...params}
            label={label}
            variant="outlined"
            required={required}
            error={showError}
            helperText={helperText}
          />
        )}
      />
    </Box>
  );
}
