import { Tooltip } from '@mui/material';
import moment from 'moment';
import { DesktopDatePicker } from '@mui/x-date-pickers/DesktopDatePicker';
import styled from 'styled-components';
import FormControl from '@mui/material/FormControl';
import { parseISO } from 'date-fns';
import get from 'lodash/get';
import { ReactElement } from 'react';

const FullWidthFormControl = styled(FormControl)`
  width: 100%;
`;

export const FormikDateField = ({
  field,
  form,
  // decoratorStart/decoratorEnd are accepted for call-site API compatibility but no longer
  // rendered; destructured here only to keep them out of the spread onto DesktopDatePicker.
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  decoratorStart,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  decoratorEnd,
  tooltip = null,
  required = false,
  dataCy = 'date-picker-filter',
  ...otherProps
}): ReactElement => {
  const isInvalid =
    get(form.errors, field.name) &&
    (get(form.touched, field.name) || form.submitCount > 0);

  let formattedValue = null;

  if (field.value && typeof field.value === 'string') {
    const match = /^(\d{4}-\d{2}-\d{2})/.exec(field.value);
    formattedValue = match ? parseISO(match[1]) : parseISO(field.value);
  }

  const datePickerComponent = (
    <FullWidthFormControl data-cy={dataCy} size="small">
      <DesktopDatePicker
        {...field}
        {...otherProps}
        label={otherProps.label}
        format="yyyy-MM-dd"
        name={field.name}
        slotProps={{
          textField: {
            size: 'small',
            error: isInvalid,
            helperText: isInvalid && get(form.errors, field.name),
            required,
            slotProps: {
              htmlInput: {
                'data-cy': `date-input-${field.name}`,
              },
            },
          },
        }}
        sx={{
          '& .MuiSvgIcon-root': {
            outline: 'none',
          },
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
