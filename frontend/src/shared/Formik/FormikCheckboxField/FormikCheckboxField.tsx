import React from 'react';
import {
  FormControlLabel,
  Checkbox,
  Box,
  FormHelperText,
} from '@material-ui/core';
import get from "lodash/get";

export const Check = ({
  field,
  form,
  label,
  ...otherProps
}): React.ReactElement => {
  const handleChange = (): void => {
    form.setFieldValue(field.name, !field.value);
  };
  const isInvalid =
    get(form.errors, field.name) &&
    (get(form.touched, field.name) ||form.submitCount>0);
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
        <FormHelperText error>{get(form.errors, field.name)}</FormHelperText>
      )}
    </Box>
  );
};
