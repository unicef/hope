import { Box } from '@material-ui/core';
import { KeyboardDatePicker } from '@material-ui/pickers';
import moment from 'moment';
import React from 'react';
import { FieldLabel } from './FieldLabel';

export const DatePickerFilter = ({
  topLabel = null,
  onChange,
  value = null,
  fullWidth = true,
  ...props
}): React.ReactElement => {
  const datePickerValue = value ? moment(value) : null;

  return (
    <Box display='flex' flexDirection='column'>
      {topLabel ? <FieldLabel>{topLabel}</FieldLabel> : null}
      <Box display='inline-flex'>
        <KeyboardDatePicker
          variant='inline'
          inputVariant='outlined'
          margin='dense'
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
          format='YYYY-MM-DD'
          InputAdornmentProps={{ position: 'end' }}
          fullWidth={fullWidth}
          helperText={null}
          {...props}
        />
      </Box>
    </Box>
  );
};
