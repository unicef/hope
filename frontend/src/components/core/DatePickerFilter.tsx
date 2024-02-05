import { Box } from '@mui/material';
import { KeyboardDatePicker } from '@material-ui/pickers';
import moment from 'moment';
import React from 'react';
import { FieldLabel } from './FieldLabel';

export const DatePickerFilter = ({
  topLabel = null,
  onChange,
  value = null,
  fullWidth = true,
  dataCy = 'date-picker-filter',
  ...props
}): React.ReactElement => {
  const datePickerValue = value ? moment(value) : null;

  return (
    <Box display="flex" flexDirection="column">
      {topLabel ? <FieldLabel>{topLabel}</FieldLabel> : null}
      <KeyboardDatePicker
        variant="inline"
        inputVariant="outlined"
        data-cy={dataCy}
        margin="dense"
        autoOk
        onChange={(date, inputString) => {
          if (date?.valueOf()) {
            const momentDate = moment(date);
            onChange(momentDate?.toISOString());
          }
          if (!inputString) {
            onChange(null);
          }
        }}
        value={datePickerValue}
        format="YYYY-MM-DD"
        InputAdornmentProps={{ position: 'end' }}
        KeyboardButtonProps={{
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          ...({ 'data-cy': 'calendar-icon' } as any),
        }}
        fullWidth={fullWidth}
        {...props}
      />
    </Box>
  );
};
