import React from 'react';
import {
  FormControlLabel,
  Checkbox,
  Box,
  FormHelperText,
} from '@material-ui/core';

export const Check = ({
  field,
  form,
  label,
  ...otherProps
}): React.ReactElement => {
  const handleChange = (): void => {
    form.setFieldValue(field.name, !field.value);
  };
  const isInvalid = form.errors[field.name] && form.touched[field.name];
  return (
    <Box flexDirection='column'>
      <FormControlLabel
        control={
          <Checkbox
            {...otherProps}
            color='primary'
            checked={field.value}
            onChange={handleChange}
          />
        }
        label={label}
      />
      {isInvalid && form.errors[field.name] && (
        <FormHelperText error>{form.errors[field.name]}</FormHelperText>
      )}
    </Box>
  );
};
