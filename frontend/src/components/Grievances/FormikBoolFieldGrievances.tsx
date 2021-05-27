import React, {useEffect} from 'react';
import {FormControl, FormHelperText, InputLabel, MenuItem, Select,} from '@material-ui/core';
import get from 'lodash/get';

const toExternalValue = (internalValue) => {
  switch (internalValue) {
    case 'YES':
      return true;
    case 'NO':
      return false;
    default:
      return null;
  }
};
export const FormikBoolFieldGrievances = ({
  field,
  form,
  multiple,
  required,
  ...otherProps
}): React.ReactElement => {
  const isInvalid =
    get(form.errors, field.name) &&
    (get(form.touched, field.name) || form.submitCount > 0);
  const options: { key: string; value: string }[] = [
    { key: 'Yes', value: 'YES' },
    { key: 'No', value: 'NO' },
  ];
  if (!required) {
    options.push({ key: 'None', value: '' });
  }
  let value;
  switch (field.value) {
    case false:
      value = 'NO';
      break;
    case true:
      value = 'YES';
      break;
    default:
      value = '';
  }
  useEffect(() => {
    if (field.value === '') {
      form.setFieldValue(field.name, toExternalValue(field.value));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [field.value]);
  const handleChange = (event): void => {
    const targetValue = event.target.value;
    const correctValue = toExternalValue(targetValue);
    form.setFieldValue(field.name, correctValue);
  };
  return (
    <>
      <FormControl variant='outlined' margin='dense' fullWidth {...otherProps}>
        <InputLabel>{otherProps.label}</InputLabel>
        <Select
          {...field}
          {...otherProps}
          name={field.name}
          onChange={handleChange}
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
          {options.map((each, index) => (
            <MenuItem
              key={each.value}
              value={each.value}
              data-cy={`select-option-${index}`}
            >
              {each.key}
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
