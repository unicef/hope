import { TextField, Box } from '@material-ui/core';
import Autocomplete from '@material-ui/lab/Autocomplete';
import React, { useState } from 'react';

export const FormikAutocomplete = ({
  field,
  form,
  choices,
  label,
}): React.ReactElement => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [value, setValue] = useState(null);
  const realSelectedValue = choices.find((item) => item.value === value);

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
        id='combo-box-demo'
        options={choices}
        onChange={handleChange}
        value={realSelectedValue}
        getOptionLabel={(choice) => choice.labelEn}
        renderInput={(params) => (
          <TextField {...params} label={label} variant='outlined' />
        )}
      />
    </Box>
  );
};
