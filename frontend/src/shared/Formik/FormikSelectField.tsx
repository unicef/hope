import React from 'react';
import { FormControl, MenuItem, InputLabel, Select } from '@material-ui/core';

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
      <FormControl variant='filled' margin='dense' fullWidth>
        <InputLabel>{otherProps.label}</InputLabel>
        <Select
          {...field}
          name={field.name}
          id={`textField-${field.name}`}
          error={isInvalid}
          helperText={isInvalid && form.errors[field.name]}
        >
          <MenuItem value=''>
            <em>None</em>
          </MenuItem>
          {otherProps.choices.map((each) => (
            <MenuItem value={each[0]}>{each[1]}</MenuItem>
          ))}
        </Select>
      </FormControl>
    </>
  );
};
