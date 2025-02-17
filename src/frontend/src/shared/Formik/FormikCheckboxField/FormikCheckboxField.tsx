import { ReactElement, useEffect } from 'react';
import {
  FormControlLabel,
  Checkbox,
  FormHelperText,
  Grid2 as Grid,
} from '@mui/material';
import get from 'lodash/get';
import { LabelizedField } from '@components/core/LabelizedField';

export function Check({
  field,
  form,
  label,
  initValue,
  displayValue = '',
  container = true,
  ...otherProps
}): ReactElement {
  const handleChange = (): void => {
    form.setFieldValue(field.name, !field.value);
  };
  const isInvalid =
    get(form.errors, field.name) &&
    (get(form.touched, field.name) || form.submitCount > 0);
  useEffect(() => {
    if (initValue !== null && initValue !== undefined) {
      form.setFieldValue(field.name, initValue);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initValue]);
  let checked = field.value;
  if (typeof checked === 'string') {
    checked = false;
  }
  useEffect(() => {
    if (typeof checked === 'string') {
      form.setFieldValue(field.name, false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [checked]);
  return (
    <Grid container={container}>
      <FormControlLabel
        control={
          <Checkbox
            {...otherProps}
            color="primary"
            checked={checked}
            onChange={handleChange}
            data-cy={`input-${field.name}`}
          />
        }
        label={displayValue ? '' : label}
        style={{ whiteSpace: 'nowrap' }}
      />
      {displayValue && (
        <Grid size={{ xs:9 }}>
          <LabelizedField label={label}>{displayValue}</LabelizedField>
        </Grid>
      )}
      {isInvalid && get(form.errors, field.name) && (
        <FormHelperText error data-cy="checkbox-error">
          {get(form.errors, field.name)}
        </FormHelperText>
      )}
    </Grid>
  );
}
