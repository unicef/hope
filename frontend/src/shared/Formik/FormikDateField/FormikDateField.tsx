import * as React from 'react';
import { InputAdornment, Tooltip, TextField } from '@mui/material';
import moment from 'moment';
import { DesktopDatePicker } from '@mui/x-date-pickers/DesktopDatePicker';
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
  required = false,
  dataCy = 'date-picker-filter',
  ...otherProps
}): React.ReactElement => {
  const isInvalid =
    get(form.errors, field.name) &&
    (get(form.touched, field.name) || form.submitCount > 0);

  let formattedValue = null;

  if (field.value && typeof field.value === 'string') {
    formattedValue = parseISO(field.value);
  }

  const datePickerComponent = (
    <FullWidthFormControl data-cy={dataCy} size="small">
      <DesktopDatePicker
        {...field}
        {...otherProps}
        label={required ? `${otherProps.label}*` : otherProps.label}
        format="yyyy-MM-dd"
        name={field.name}
        slotProps={{
          textField: {
            size: 'small',
            error: isInvalid,
            helperText: isInvalid && get(form.errors, field.name),
          },
        }}
        sx={{
          '& .MuiSvgIcon-root': {
            outline: 'none',
          },
        }}
        slots={{
          TextField: (props) => (
            <TextField
              {...props}
              variant="outlined"
              size="small"
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
              required={required}
              // https://github.com/mui-org/material-ui/issues/12805
              // eslint-disable-next-line react/jsx-no-duplicate-props
              inputProps={{
                'data-cy': `date-input-${field.name}`,
              }}
            />
          ),
        }}
        value={formattedValue || null}
        onBlur={() => {
          setTimeout(() => {
            form.handleBlur({ target: { name: field.name } });
          }, 0);
        }}
        onChange={(date) => {
          if (date instanceof Date && !isNaN(date.getTime())) {
            field.onChange({
              target: {
                value: moment(date).format('YYYY-MM-DD'),
                name: field.name,
              },
            });
          } else {
            console.error('Invalid date:', date);
            field.onChange({
              target: {
                value: null,
                name: field.name,
              },
            });
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
