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
  ...otherProps
}): React.ReactElement => {
  const isInvalid = form.errors[field.name] && form.touched[field.name];
  return (
    <>
      <FormControl variant='filled' margin='dense' fullWidth {...otherProps}>
        <InputLabel>{otherProps.label}</InputLabel>
        <Select
          {...field}
          {...otherProps}
          name={field.name}
          value={field.value || field.name}
          id={`textField-${field.name}`}
          error={isInvalid}
        >
          {otherProps.choices.map((each) => (
            <MenuItem
              key={each.value ? each.value : each.name}
              value={each.value ? each.value : each.name}
            >
              {each.label ? each.label : each.name}
            </MenuItem>
          ))}
        </Select>
        {isInvalid && form.errors[field.name] && (
          <FormHelperText error>{form.errors[field.name]}</FormHelperText>
        )}
      </FormControl>
    </>
  );
};
