import { Autocomplete, Chip, FormHelperText, TextField, Tooltip } from '@mui/material';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

interface Choice {
  value: string;
  name: string;
}

interface FormikChipAutocompleteProps {
  field: { name: string; value: string[] };
  form: {
    setFieldValue: (name: string, value: any) => void;
    errors: any;
    touched: any;
  };
  label?: string;
  choices: Choice[];
  lockedValues?: string[];
  disabled?: boolean;
  required?: boolean;
  [key: string]: any;
}

export function FormikChipAutocomplete({
  field,
  form,
  label,
  choices,
  lockedValues = [],
  disabled,
  required,
  ...rest
}: FormikChipAutocompleteProps): ReactElement {
  const dataCy = rest['data-cy'];
  const { t } = useTranslation();
  const error =
    form.touched[field.name] && form.errors[field.name]
      ? String(form.errors[field.name])
      : undefined;

  const selectedOptions = (field.value || []).map(
    (id) => choices.find((c) => c.value === id) ?? { value: id, name: id },
  );

  return (
    <>
      <Autocomplete
        multiple
        options={choices}
        value={selectedOptions}
        isOptionEqualToValue={(opt, val) => opt.value === val.value}
        getOptionLabel={(opt) => opt.name || opt.value}
        onChange={(_, newValue: Choice[]) => {
          const newIds = newValue.map((o) => o.value);
          const missing = lockedValues.filter((v) => !newIds.includes(v));
          form.setFieldValue(field.name, [...newIds, ...missing]);
        }}
        renderTags={(tagValues, getTagProps) =>
          tagValues.map((option, index) => {
            const isLocked = lockedValues.includes(option.value);
            const { key, ...tagProps } = getTagProps({ index });
            const chip = (
              <Chip
                key={key}
                label={option.name}
                {...tagProps}
                onDelete={isLocked ? undefined : tagProps.onDelete}
              />
            );
            return isLocked ? (
              <Tooltip
                key={key}
                title={t('Already used in a Payment Plan')}
                arrow
              >
                <span>{chip}</span>
              </Tooltip>
            ) : chip;
          })
        }
        renderInput={(params) => (
          <TextField
            {...params}
            label={label}
            variant="outlined"
            size="small"
            required={required}
            error={!!error}
            data-cy={dataCy}
          />
        )}
        disabled={disabled}
      />
      {error && <FormHelperText error>{error}</FormHelperText>}
    </>
  );
}
