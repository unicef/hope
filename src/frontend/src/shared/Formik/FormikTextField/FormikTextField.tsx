import { InputAdornment, TextField } from '@mui/material';
import styled from 'styled-components';
import get from 'lodash/get';
import { ReactElement } from 'react';

const StyledTextField = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
  .MuiFormHelperText-root {
    white-space: pre-line;
  }
`;

export function FormikTextField({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  type,
  precision,
  integer,
  maxLength,
  ...otherProps
}): ReactElement {
  const isInvalid = Boolean(
    get(form.errors, field.name) &&
      (get(form.touched, field.name) || form.submitCount > 0 || form.errors),
  );

  const handleKeyPress = (evt): void => {
    if (type === 'number' && ['e', 'E', '+', '-'].includes(evt.key)) {
      evt.preventDefault();
    }
    if (integer && [',', '.'].includes(evt.key)) {
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

  const handleChange = (e): void => {
    if (type === 'number' && e.target.value > 999999999) {
      return;
    }
    form.handleChange(e);
  };

  return (
    <StyledTextField
      {...field}
      {...otherProps}
      name={field.name}
      id={`textField-${field.name}`}
      size="small"
      value={field.value}
      onChange={handleChange}
      onBlur={onBlur}
      error={isInvalid}
      autoComplete="off"
      type={type}
      helperText={isInvalid && get(form.errors, field.name)}
      label={otherProps.label} // pass the label directly to the StyledTextField
      slotProps={{
        input: {
          onKeyPress: handleKeyPress,
          startAdornment: decoratorStart && (
            <InputAdornment position="start">{decoratorStart}</InputAdornment>
          ),
          endAdornment: decoratorEnd && (
            <InputAdornment position="end">{decoratorEnd}</InputAdornment>
          ),
          'data-cy': `input-${field.name}`,
          maxLength: maxLength || undefined,
        },
      }}
    />
  );
}
