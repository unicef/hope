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
          value={field.value || otherProps.value}
          id={`textField-${field.name}`}
          error={isInvalid}
          SelectDisplayProps={{ 'data-cy': `select-field-collapsed-${field.name}`}}
          MenuProps={{ 'data-cy': `select-field-options-${field.name}`}}
        >
          {otherProps.choices.map((each) => (
            <MenuItem
              key={each.value ? each.value : each.name}
              value={each.value ? each.value : each.name}
            >
              {each.labelEn || each.name || each.label}
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
