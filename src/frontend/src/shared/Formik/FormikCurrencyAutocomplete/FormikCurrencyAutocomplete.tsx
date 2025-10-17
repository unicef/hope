import { TextField, Autocomplete } from '@mui/material';
import { useTranslation } from 'react-i18next';
import get from 'lodash/get';
import { ReactElement } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';

export const FormikCurrencyAutocomplete = ({
  field,
  form,
  disabled,
  ...otherProps
}): ReactElement => {
  const { t } = useTranslation();

  const { data } = useQuery({
    queryKey: ['currencies'],
    queryFn: () => RestService.restChoicesCurrenciesList(),
  });

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
    <Autocomplete
      options={data || []}
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
          size="small"
          error={isInvalid}
          helperText={`${isInvalid ? get(form.errors, field.name) : ''}`}
          {...otherProps}
        />
      )}
      data-cy="input-currency"
    />
  );
};
