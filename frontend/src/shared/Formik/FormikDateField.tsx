import React from 'react';
import { TextField, InputAdornment } from '@material-ui/core';
import { DatePicker } from '@material-ui/pickers';
import moment from 'moment';

export const FormikDateField = ({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  ...otherProps
}) => {
  const isInvalid = form.errors[field.name] && form.touched[field.name];
  const dateFormat = 'DD/MM/YYYY';
  let formattedValue = field.value === '' ? null : field.value;
  if (formattedValue) {
    formattedValue = moment(formattedValue).toISOString();
  }
  console.log('error', form.errors);
  return (
    <DatePicker
      {...field}
      {...otherProps}
      name={field.name}
      variant='inline'
      inputVariant='filled'
      margin='dense'
      value={formattedValue}
      error={isInvalid}
      onBlur={null}
      helperText={isInvalid && form.errors[field.name]}
      autoOk
      onClose={() => {
        setTimeout(() => {
          form.handleBlur({ target: { name: field.name } });
        }, 0);
      }}
      onChange={(date) => {
        field.onChange({
          target: { value: date.toISOString(), name: field.name },
        });
      }}
      format={dateFormat}
      InputProps={{

        startAdornment: decoratorStart && (
          <InputAdornment position='start'>{decoratorStart}</InputAdornment>
        ),
        endAdornment: decoratorEnd && (
          <InputAdornment position='end'>{decoratorEnd}</InputAdornment>
        ),
      }}
    />
  );
};
