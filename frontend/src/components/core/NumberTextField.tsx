import { Box, InputAdornment, TextField } from '@mui/material';
import styled from 'styled-components';
import * as React from 'react';
import { FieldLabel } from './FieldLabel';

const TextContainer = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
`;

export function NumberTextField({
  topLabel = null,
  value,
  placeholder,
  onChange,
  icon = null,
  ...otherProps
}): React.ReactElement {
  return (
    <Box display="flex" flexDirection="column">
      {topLabel ? <FieldLabel>{topLabel}</FieldLabel> : null}
      <TextContainer
        {...otherProps}
        value={value}
        size="medium"
        placeholder={placeholder}
        onChange={onChange}
        variant="outlined"
        margin="dense"
        type="number"
        InputProps={
          icon
            ? {
                startAdornment: (
                  <InputAdornment position="start">{icon}</InputAdornment>
                ),
              }
            : null
        }
      />
    </Box>
  );
}
