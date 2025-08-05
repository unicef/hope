import { Box, FormControl } from '@mui/material';
import { DesktopDatePicker } from '@mui/x-date-pickers/DesktopDatePicker';
import { parseISO } from 'date-fns';
import { FieldLabel } from './FieldLabel';
import { ReactElement } from 'react';

export const DatePickerFilter = ({
  topLabel = null,
  onChange,
  value = null,
  dataCy = 'date-picker-filter',
  ...props
}): ReactElement => {
  let datePickerValue = null;
  if (value) {
    // If value is 'YYYY-MM-DD', convert to ISO string for parseISO
    if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
      datePickerValue = parseISO(`${value}T00:00:00.000Z`);
    } else {
      datePickerValue = parseISO(value);
    }
  }
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
              // Format as 'yyyy-MM-dd' (date only)
              const year = date.getFullYear();
              const month = String(date.getMonth() + 1).padStart(2, '0');
              const day = String(date.getDate()).padStart(2, '0');
              onChange(`${year}-${month}-${day}`);
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
