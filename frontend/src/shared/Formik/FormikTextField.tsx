import React from 'react';
import { TextField, InputAdornment } from '@material-ui/core';

export const FormikTextField = ({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  ...otherProps
}) => {
  const isInvalid = form.errors[field.name] && form.touched[field.name];
  const handleKeyPress = (evt) => {
    if (
      otherProps.type === 'number' &&
      ['e', 'E', '+', '-'].includes(evt.key)
    ) {
      evt.preventDefault();
    }
  };
  return (
    <>
      <TextField
        {...field}
        {...otherProps}
        name={field.name}
        id={`textField-${field.name}`}
        variant='filled'
        margin='dense'
        value={field.value}
        onChange={form.handleChange}
        onBlur={form.handleBlur}
        error={isInvalid}
        autoComplete='off'
        helperText={isInvalid && form.errors[field.name]}
        InputProps={{
          onKeyPress: handleKeyPress,
          startAdornment: decoratorStart && (
            <InputAdornment position='start'>{decoratorStart}</InputAdornment>
          ),
          endAdornment: decoratorEnd && (
            <InputAdornment position='end'>{decoratorEnd}</InputAdornment>
          ),
        }}
        
        
      />
    </>
  );
};
