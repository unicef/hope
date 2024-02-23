import * as React from 'react';
import { InputAdornment, Tooltip, TextField } from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import styled from 'styled-components';
import FormControl from '@mui/material/FormControl';
import { parseISO } from 'date-fns';
import get from 'lodash/get';

const FullWidthFormControl = styled(FormControl)`
  width: 100%;
`;

export const FormikDateField = ({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  tooltip = null,
  ...otherProps
}): React.ReactElement => {
  console.log(form.errors);
  const isInvalid =
    get(form.errors, field.name) &&
    (get(form.touched, field.name) || form.submitCount > 0);

  let formattedValue = null;

  if (field.value && typeof field.value === 'string') {
    formattedValue = parseISO(field.value);
  }
  const datePickerComponent = (
    <FullWidthFormControl>
      <DatePicker
        {...field}
        {...otherProps}
        format="yyyy-MM-dd"
        name={field.name}
        renderInput={(params) => (
          <TextField
            {...params}
            variant="outlined"
            margin="dense"
            fullWidth
            error={isInvalid}
            helperText={isInvalid && get(form.errors, field.name)}
            InputProps={{
              startAdornment: decoratorStart && (
                <InputAdornment position="start">
                  {decoratorStart}
                </InputAdornment>
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
          if (date instanceof Date && !isNaN(date.getTime())) {
            // Date is valid
            const event = {
              target: {
                name: field.name,
                value: date,
              },
            };
            field.onChange(event);
          } else {
            // Date is not valid
            console.error('Invalid date:', date);
          }
        }}
      />
    </FullWidthFormControl>
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
