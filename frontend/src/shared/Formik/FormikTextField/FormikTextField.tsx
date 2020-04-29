import React from 'react';
import { InputAdornment, TextField } from '@material-ui/core';
import styled from 'styled-components';

const StyledTextField = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
`;

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
      <StyledTextField
        {...field}
        {...otherProps}
        name={field.name}
        id={`textField-${field.name}`}
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
