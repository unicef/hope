import React from 'react';
import { InputAdornment, Tooltip, TextField } from '@mui/material';
import DatePicker from '@mui/lab/DatePicker';
import moment from 'moment';
import get from 'lodash/get';

export const FormikDateField = ({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  tooltip = null,
  ...otherProps
}): React.ReactElement => {
  const isInvalid =
    get(form.errors, field.name) &&
    (get(form.touched, field.name) || form.submitCount > 0);
  const dateFormat = 'YYYY-MM-DD';
  let formattedValue = field.value === '' ? null : field.value;
  if (formattedValue) {
    formattedValue = moment(formattedValue).toISOString();
  }

  const datePickerComponent = (
    <DatePicker
      {...field}
      {...otherProps}
      name={field.name}
      renderInput={(params) => (
        <TextField
          {...params}
          variant="outlined"
          margin="dense"
          error={isInvalid}
          helperText={isInvalid && get(form.errors, field.name)}
          InputProps={{
            startAdornment: decoratorStart && (
              <InputAdornment position="start">{decoratorStart}</InputAdornment>
            ),
            endAdornment: decoratorEnd && (
              <InputAdornment position="end">{decoratorEnd}</InputAdornment>
            ),
          }}
          // https://github.com/mui-org/material-ui/issues/12805
          // eslint-disable-next-line react/jsx-no-duplicate-props
          inputProps={{
            'data-cy': `date-input-${field.name}`,
          }}
        />
      )}
      value={formattedValue || null}
      onBlur={() => {
        setTimeout(() => {
          form.handleBlur({ target: { name: field.name } });
        }, 0);
      }}
      onChange={(date) => {
        if (date) {
          field.onChange({
            target: {
              value: moment(date).format('YYYY-MM-DD') || null,
              name: field.name,
            },
          });
        }
      }}
      format={dateFormat}
    />
  );

  if (tooltip) {
    return (
      <Tooltip title={tooltip}>
        <div>{datePickerComponent}</div>
      </Tooltip>
    );
  }
  return datePickerComponent;
};
