import { Box, FormControl } from '@mui/material';
import { DesktopDatePicker } from '@mui/x-date-pickers/DesktopDatePicker';
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
  const calculatedDataCy =
    dataCy === 'date-picker-filter'
      ? `date-picker-filter-${props?.label || props?.placeholder || ''}`
      : dataCy;

  return (
    <Box display="flex" flexDirection="column">
      {topLabel ? <FieldLabel>{topLabel}</FieldLabel> : null}
      <FormControl data-cy={calculatedDataCy} size="small">
        <DesktopDatePicker
          slotProps={{ textField: { size: 'small' } }}
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
      </FormControl>
    </Box>
  );
};
