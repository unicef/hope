import { Box, TextField, InputAdornment } from '@mui/material';
import DatePicker from '@mui/lab/DatePicker';
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
  const datePickerValue = value ? moment(value).toISOString() : null;

  return (
    <Box display="flex" flexDirection="column">
      {topLabel ? <FieldLabel>{topLabel}</FieldLabel> : null}
      <DatePicker
        renderInput={(params) => (
          <TextField
            {...params}
            variant="outlined"
            margin="dense"
            InputAdornmentProps={{ position: 'end' }}
            fullWidth={fullWidth}
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            inputProps={{ ...params.inputProps, 'data-cy': dataCy }}
            InputProps={{
              ...params.InputProps,
              endAdornment: (
                <InputAdornment position="end">
                  {params.InputProps.endAdornment}
                </InputAdornment>
              ),
            }}
          />
        )}
        autoOk
        onChange={(date) => {
          if (date) {
            onChange(moment(date).toISOString());
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
