import Autocomplete from '@mui/lab/Autocomplete';
import { Box, TextField } from '@mui/material';
import * as React from 'react';

export function FormikAutocomplete({
  field,
  form,
  choices,
  label,
}): React.ReactElement {
  const realSelectedValue = choices.find((item) => item.value === field.value);

  const handleChange = (e, option): void => {
    if (!option) {
      form.setFieldValue(field.name, null);
    } else {
      form.setFieldValue(field.name, option.value);
    }
  };

  return (
    <Box mt={2}>
      <Autocomplete
        id="combo-box-demo"
        options={choices}
        onChange={handleChange}
        value={realSelectedValue}
        getOptionLabel={(choice) => choice.labelEn}
        renderInput={(params) => (
          <TextField {...params} label={label} variant="outlined" />
        )}
      />
    </Box>
  );
}
