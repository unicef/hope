import { Box } from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import React from 'react';
import TextField from '../../shared/TextField';
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
      <DatePicker
        label={label}
        value={value || null}
        onChange={onChange}
        renderInput={(params) => (
          <TextField placeholder={placeholder} {...params} />
        )}
      />
    </Box>
  );
}
