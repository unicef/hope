import React from 'react';
import { InputAdornment, TextField } from '@material-ui/core';
import styled from 'styled-components';
import get from 'lodash/get';

const StyledTextField = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
`;

export const FormikDecimalField = ({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  ...otherProps
}): React.ReactElement => {
  const isInvalid =
    get(form.errors, field.name) &&
    (get(form.touched, field.name) || form.submitCount > 0);
  const handleKeyPress = (evt): void => {
    if (['e', 'E', '+', '-'].includes(evt.key)) {
      evt.preventDefault();
    }
  };

  function handleChange(e): void {
    form.setFieldValue(field.name, e.target.value.toString(), true);
  }

  return (
    <>
      <StyledTextField
        {...field}
        {...otherProps}
        name={field.name}
        id={`textField-${field.name}`}
        margin='dense'
        value={field.value}
        onChange={handleChange}
        error={isInvalid}
        autoComplete='off'
        type='number'
        helperText={isInvalid && get(form.errors, field.name)}
        InputProps={{
          onKeyPress: handleKeyPress,
          startAdornment: decoratorStart && (
            <InputAdornment position='start'>{decoratorStart}</InputAdornment>
          ),
          endAdornment: decoratorEnd && (
            <InputAdornment position='end'>{decoratorEnd}</InputAdornment>
          ),
        }}
        // https://github.com/mui-org/material-ui/issues/12805
        // eslint-disable-next-line react/jsx-no-duplicate-props
        inputProps={{
          'data-cy': `input-${field.name}`,
        }}
      />
    </>
  );
};
