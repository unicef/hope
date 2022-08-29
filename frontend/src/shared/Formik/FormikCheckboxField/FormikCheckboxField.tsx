import React, { useEffect } from 'react';
import {
  FormControlLabel,
  Checkbox,
  FormHelperText,
  Grid,
} from '@material-ui/core';
import get from 'lodash/get';
import styled from 'styled-components';
import { LabelizedField } from '../../../components/core/LabelizedField';

const Width80 = styled.div`
  width: 80%;
`;

export const Check = ({
  field,
  form,
  label,
  initValue,
  displayValue = '',
  ...otherProps
}): React.ReactElement => {
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
    <Grid container>
      <FormControlLabel
        control={
          <Checkbox
            {...otherProps}
            color='primary'
            checked={checked}
            onChange={handleChange}
          />
        }
        label={displayValue ? '' : label}
      />
      {displayValue && (
        <Width80>
          <LabelizedField label={label}>{displayValue}</LabelizedField>
        </Width80>
      )}
      {isInvalid && get(form.errors, field.name) && (
        <FormHelperText error>{get(form.errors, field.name)}</FormHelperText>
      )}
    </Grid>
  );
};
