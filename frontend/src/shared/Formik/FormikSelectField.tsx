import React from 'react';
import {
  FormControl,
  FormHelperText,
  MenuItem,
  InputLabel,
  Select,
} from '@material-ui/core';

export const FormikSelectField = ({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  ...otherProps
}) => {
  const isInvalid = form.errors[field.name] && form.touched[field.name];
  return (
    <>
      <FormControl variant='filled' margin='dense' fullWidth {...otherProps}>
        <InputLabel>{otherProps.label}</InputLabel>
        <Select
          {...field}
          {...otherProps}
          name={field.name}
          value={field.value}
          id={`textField-${field.name}`}
          error={isInvalid}
          helperText={isInvalid && form.errors[field.name]}
        >
          {otherProps.choices.map((each, index) => (
            <MenuItem key={each.value} value={each.value}>
              {each.name}
            </MenuItem>
          ))}
        </Select>
          {isInvalid && form.errors[field.name] && <FormHelperText error>{form.errors[field.name]}</FormHelperText>}
      </FormControl>
    </>
  );
};
