import { Autocomplete, Chip, FormHelperText, TextField } from '@mui/material';
import { ReactElement } from 'react';

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
  disabled?: boolean;
  required?: boolean;
  [key: string]: any;
}

export function FormikChipAutocomplete({
  field,
  form,
  label,
  choices,
  disabled,
  required,
}: FormikChipAutocompleteProps): ReactElement {
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
          form.setFieldValue(
            field.name,
            newValue.map((o) => o.value),
          );
        }}
        renderTags={(tagValues, getTagProps) =>
          tagValues.map((option, index) => {
            const { key, ...tagProps } = getTagProps({ index });
            return <Chip key={key} label={option.name} {...tagProps} />;
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
          />
        )}
        disabled={disabled}
      />
      {error && <FormHelperText error>{error}</FormHelperText>}
    </>
  );
}
