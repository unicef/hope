import { Box, FormControl } from '@mui/material';
import { DesktopDatePicker } from '@mui/x-date-pickers/DesktopDatePicker';
import { format, parseISO } from 'date-fns';
import { FieldLabel } from './FieldLabel';
import { ReactElement } from 'react';

export const DatePickerFilter = ({
  topLabel = null,
  onChange,
  value = null,
  dataCy = 'date-picker-filter',
  ...props
}): ReactElement => {
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
          //Necessary for selenium to find the input field
          enableAccessibleFieldDOMStructure={false}
          slotProps={{ textField: { size: 'small' } }}
          onChange={(value) => {
            if (value instanceof Date && !isNaN(value.getTime())) {
              onChange(format(value, 'yyyy-MM-dd'));
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
