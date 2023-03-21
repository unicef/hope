import { Box } from '@material-ui/core';
import { KeyboardDatePicker, KeyboardDatePickerProps } from '@material-ui/pickers';
import React from 'react';
import { FieldLabel } from './FieldLabel';

export interface DatePickerFieldProps extends KeyboardDatePickerProps {
  topLabel?: string | null;
}

export function DatePickerFilter({
  topLabel = null,
  onChange,
  value = null,
  ...props
}: DatePickerFieldProps): React.ReactElement {
  return (
    <Box display='flex' flexDirection='column'>
      {topLabel ? <FieldLabel>{topLabel}</FieldLabel> : null}
      <KeyboardDatePicker
        variant='inline'
        inputVariant='outlined'
        margin='dense'
        autoOk
        onChange={onChange}
        value={value}
        format='YYYY-MM-DD'
        InputAdornmentProps={{ position: 'end' }}
        {...props}
      />
    </Box>
  );
}
