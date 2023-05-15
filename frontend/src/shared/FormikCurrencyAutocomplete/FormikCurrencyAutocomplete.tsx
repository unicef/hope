import { Box } from '@material-ui/core';
import Autocomplete from '@material-ui/lab/Autocomplete';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import get from 'lodash/get';
import { useCurrencyChoicesQuery } from '../../__generated__/graphql';
import TextField from '../TextField';

const StyledAutocomplete = styled(Autocomplete)`
  width: ${(props) => (props.fullWidth ? '100%' : '232px')}
    .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export const FormikCurrencyAutocomplete = ({
  field,
  form,
  disabled,
  ...otherProps
}): React.ReactElement => {
  const { t } = useTranslation();

  const { data } = useCurrencyChoicesQuery();

  const handleChange = (e, option): void => {
    if (!option) {
      form.setFieldValue(field.name, null);
    } else {
      form.setFieldValue(field.name, option.value);
    }
  };

  const isInvalid =
    get(form.errors, field.name) &&
    (get(form.touched, field.name) || form.submitCount > 0);

  if (!data) return null;

  return (
    <Box mt={1}>
      <StyledAutocomplete
        options={data?.currencyChoices || []}
        defaultValue={field.value}
        getOptionLabel={(option) => option.name}
        onChange={handleChange}
        disabled={disabled}
        fullWidth
        renderInput={(params) => (
          <TextField
            {...params}
            label={t('Currency')}
            variant='outlined'
            margin='dense'
            error={isInvalid}
            helperText={`${isInvalid ? get(form.errors, field.name) : ''}`}
            {...otherProps}
          />
        )}
        data-cy='input-currency'
      />
    </Box>
  );
};
