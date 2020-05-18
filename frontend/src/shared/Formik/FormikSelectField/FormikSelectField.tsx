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
      <FormControl variant='outlined' margin='dense' fullWidth {...otherProps}>
        <InputLabel>{otherProps.label}</InputLabel>
        <Select
          {...field}
          {...otherProps}
          name={field.name}
          value={field.value || otherProps.value}
          id={`textField-${field.name}`}
          error={isInvalid}
          SelectDisplayProps={{ 'data-cy': `select-${field.name}`}}
          MenuProps={{ 'data-cy': `select-options-${field.name}`}}
        >
          {otherProps.choices.map((each, index) => (
            <MenuItem
              key={each.value ? each.value : each.name}
              value={each.value ? each.value : each.name}
              data-cy={`select-option-${index}`}
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
