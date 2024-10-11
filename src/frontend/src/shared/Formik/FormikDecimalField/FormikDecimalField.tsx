import * as React from 'react';
import styled from 'styled-components';
import get from 'lodash/get';
import { TextField, InputAdornment } from '@mui/material';

const StyledTextField = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
`;

export function FormikDecimalField({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  ...otherProps
}): React.ReactElement {
  const isInvalid =
    get(form.errors, field.name) &&
    (get(form.touched, field.name) || form.submitCount > 0);
  const handleKeyPress = (evt): void => {
    if (['e', 'E', '+', '-'].includes(evt.key)) {
      evt.preventDefault();
    }
  };

  const handleChange = (e): void => {
    if (e.target.value > 999999999) {
      return;
    }
    form.setFieldValue(field.name, e.target.value.toString(), true);
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
      error={isInvalid}
      autoComplete="off"
      type="number"
      helperText={isInvalid && get(form.errors, field.name)}
      InputProps={{
        onKeyPress: handleKeyPress,
        startAdornment: decoratorStart && (
          <InputAdornment position="start">{decoratorStart}</InputAdornment>
        ),
        endAdornment: decoratorEnd && (
          <InputAdornment position="end">{decoratorEnd}</InputAdornment>
        ),
      }}
      // https://github.com/mui-org/material-ui/issues/12805
      // eslint-disable-next-line react/jsx-no-duplicate-props
      inputProps={{
        'data-cy': `input-${field.name}`,
      }}
    />
  );
}
