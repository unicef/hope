import { Box } from '@material-ui/core';
import { KeyboardDatePicker } from '@material-ui/pickers';
import React from 'react';
import { FieldLabel } from './FieldLabel';

export function DatePickerFilter({
  label = null,
  onChange,
  value,
  topLabel = null,
  placeholder = null,
}): React.ReactElement {
  return (
    <Box display='flex' flexDirection='column'>
      {topLabel ? <FieldLabel>{topLabel}</FieldLabel> : null}
      <KeyboardDatePicker
        variant='inline'
        inputVariant='outlined'
        margin='dense'
        label={label}
        placeholder={placeholder}
        autoOk
        onChange={onChange}
        value={value || null}
        format='YYYY-MM-DD'
        InputAdornmentProps={{ position: 'end' }}
      />
    </Box>
  );
}
