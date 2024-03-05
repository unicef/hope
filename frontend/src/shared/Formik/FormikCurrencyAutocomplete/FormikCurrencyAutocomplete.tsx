import { Box, TextField } from '@mui/material';
import Autocomplete from '@mui/lab/Autocomplete';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import get from 'lodash/get';
import { useCurrencyChoicesQuery } from '@generated/graphql';

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
      <Autocomplete
        options={data?.currencyChoices || []}
        defaultValue={field.value}
        getOptionLabel={(option: any) => option.name}
        onChange={handleChange}
        disabled={disabled}
        fullWidth
        renderInput={(params) => (
          <TextField
            {...params}
            label={t('Currency')}
            variant="outlined"
            error={isInvalid}
            helperText={`${isInvalid ? get(form.errors, field.name) : ''}`}
            {...otherProps}
          />
        )}
        data-cy="input-currency"
      />
    </Box>
  );
};
