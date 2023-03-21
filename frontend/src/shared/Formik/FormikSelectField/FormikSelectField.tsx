import React from 'react';
import {
  FormControl,
  FormHelperText,
  MenuItem,
  InputLabel,
  Select,
} from '@material-ui/core';
import get from 'lodash/get';

export const FormikSelectField = ({
  field,
  form,
  multiple,
  ...otherProps
}): React.ReactElement => {
  const isInvalid =
    get(form.errors, field.name) &&
    (get(form.touched, field.name) || form.submitCount > 0);
  const value = multiple
    ? field.value || otherProps.value || []
    : field.value || otherProps.value || '';

  return (
    <>
      <FormControl variant='outlined' margin='dense' fullWidth {...otherProps}>
        <InputLabel>{otherProps.label}</InputLabel>
        <Select
          {...field}
          {...otherProps}
          name={field.name}
          multiple={multiple}
          value={value}
          id={`textField-${field.name}`}
          error={isInvalid}
          SelectDisplayProps={{ 'data-cy': `select-${field.name}` }}
          MenuProps={{
            'data-cy': `select-options-${field.name}`,
            MenuListProps: { 'data-cy': 'select-options-container' },
          }}
        >
          {otherProps.choices.map((each) => (
            <MenuItem
              key={each.value ? each.value : each.name || ''}
              value={each.value ? each.value : each.name || ''}
              data-cy={`select-option-${each.name}`}
              disabled={each.disabled || false}
            >
              {each.labelEn || each.name || each.label}
            </MenuItem>
          ))}
        </Select>
        {isInvalid && (
          <FormHelperText error>{get(form.errors, field.name)}</FormHelperText>
        )}
      </FormControl>
    </>
  );
};
