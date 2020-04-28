import React from 'react';
import { TextField, InputAdornment } from '@material-ui/core';
import Autocomplete from '@material-ui/lab/Autocomplete';

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

export const FormikTagsSelectField = ({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  label,
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
      <Autocomplete
        {...field}
        {...otherProps}
        multiple
        name={field.name}
        id='tags-standard'
        options={[]}
        value={field.value}
        onChange={form.handleChange}
        freeSolo
        placeholder={label}
        renderInput={(params) => {
          return (
            <TextField
              {...params}
              id={`textField-${field.name}`}
              margin='dense'
              onBlur={onBlur}
              error={isInvalid}
              helperText={isInvalid && form.errors[field.name]}
              variant='filled'
              label={label}
            />
          );
        }}
      />
    </>
  );
};
