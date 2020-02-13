import React from 'react';
import { TextField, InputAdornment } from '@material-ui/core';

export const FormikTextField = ({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  type,
  precision,
  ...otherProps
}): React.ReactElement => {
  const isInvalid = form.errors[field.name] && form.touched[field.name];
  const handleKeyPress = (evt): void => {
    if (
      otherProps.type === 'number' &&
      ['e', 'E', '+', '-'].includes(evt.key)
    ) {
      evt.preventDefault();
    }
  };

  const onBlur = (e): void => {
    const newEvent = { ...e };
    if (type === 'number' && precision !== undefined) {
      newEvent.target.value = parseFloat(e.target.value).toFixed(2);
    }
    form.handleBlur(newEvent);
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
        onBlur={onBlur}
        error={isInvalid}
        autoComplete='off'
        type={type}
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
