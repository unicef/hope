import { Box } from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { formatISO, parseISO } from 'date-fns';
import * as React from 'react';
import { FieldLabel } from './FieldLabel';

export const DatePickerFilter = ({
  topLabel = null,
  onChange,
  value = null,
  dataCy = 'date-picker-filter',
  ...props
}): React.ReactElement => {
  const datePickerValue = value ? parseISO(value) : null;

  return (
    <Box display="flex" flexDirection="column">
      {topLabel ? <FieldLabel>{topLabel}</FieldLabel> : null}
      <DatePicker
        data-y={dataCy}
        onChange={(date) => {
          if (date) {
            onChange(formatISO(date));
          } else {
            onChange(null);
          }
        }}
        value={datePickerValue || null}
        format="yyyy-MM-dd"
        {...props}
      />
    </Box>
  );
};
