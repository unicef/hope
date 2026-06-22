import {
  Autocomplete,
  Chip,
  FormHelperText,
  TextField,
  Tooltip,
} from '@mui/material';
import { FieldInputProps, FormikProps } from 'formik';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

interface Choice {
  value: string;
  name: string;
}

interface FormikChipAutocompleteProps {
  field: FieldInputProps<string[]>;
  form: FormikProps<unknown>;
  label?: string;
  /** Options used to resolve the labels of already-selected chips. */
  choices: Choice[];
  /**
   * Options shown in the dropdown. Defaults to `choices`; pass separately when
   * the dropdown is driven by a server-side search but selected chips must keep
   * their labels from an accumulated set.
   */
  options?: Choice[];
  lockedValues?: string[];
  disabled?: boolean;
  required?: boolean;
  loading?: boolean;
  inputValue?: string;
  onInputChange?: (value: string) => void;
  /** Disable client-side filtering when the options are filtered server-side. */
  serverSide?: boolean;
  'data-cy'?: string;
}

export function FormikChipAutocomplete({
  field,
  form,
  label,
  choices,
  options,
  lockedValues = [],
  disabled,
  required,
  loading,
  inputValue,
  onInputChange,
  serverSide = false,
  'data-cy': dataCy,
}: FormikChipAutocompleteProps): ReactElement {
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
        options={options ?? choices}
        value={selectedOptions}
        loading={loading}
        inputValue={inputValue}
        filterOptions={serverSide ? (opts: Choice[]) => opts : undefined}
        onInputChange={(_, newVal, reason) => {
          if (onInputChange && reason !== 'reset') onInputChange(newVal);
        }}
        isOptionEqualToValue={(opt, val) => opt.value === val.value}
        getOptionLabel={(opt) => opt.name || opt.value}
        getOptionDisabled={(opt) => lockedValues.includes(opt.value)}
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
            ) : (
              chip
            );
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
