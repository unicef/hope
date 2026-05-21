import { useBaseUrl } from '@hooks/useBaseUrl';
import { useDebounce } from '@hooks/useDebounce';
import {
  Autocomplete,
  Chip,
  FormHelperText,
  TextField,
  Tooltip,
} from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

interface Choice {
  value: string;
  name: string;
}

interface PaymentPlanPurposesAutocompleteProps {
  field: { name: string; value: string[] };
  form: {
    setFieldValue: (name: string, value: any) => void;
    errors: any;
    touched: any;
  };
  lockedValues?: string[];
  disabled?: boolean;
  required?: boolean;
}

export function PaymentPlanPurposesAutocomplete({
  field,
  form,
  lockedValues = [],
  disabled,
  required,
}: PaymentPlanPurposesAutocompleteProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const [inputValue, setInputValue] = useState('');
  const debouncedSearch = useDebounce(inputValue, 800);
  const [knownOptions, setKnownOptions] = useState<Choice[]>([]);

  const { data: fetchedOptions = [], isLoading } = useQuery({
    queryKey: ['paymentPlanPurposes', businessArea, debouncedSearch],
    queryFn: () =>
      (RestService as any).restBusinessAreasPaymentPlanPurposesList({
        businessAreaSlug: businessArea,
        search: debouncedSearch || undefined,
      }),
    select: (d: any) =>
      (d?.results ?? []).map((p: any) => ({ value: p.id, name: p.name })),
  });

  // Accumulate seen options so selected chips keep their names when search changes
  useEffect(() => {
    if (fetchedOptions.length > 0) {
      setKnownOptions((prev) => {
        const merged = [...prev];
        for (const opt of fetchedOptions) {
          if (!merged.find((o) => o.value === opt.value)) {
            merged.push(opt);
          }
        }
        return merged;
      });
    }
  }, [fetchedOptions]);

  const selectedOptions = (field.value || []).map(
    (id) => knownOptions.find((o) => o.value === id) ?? { value: id, name: id },
  );

  const error =
    form.touched[field.name] && form.errors[field.name]
      ? String(form.errors[field.name])
      : undefined;

  return (
    <>
      <Autocomplete
        multiple
        filterOptions={(x) => x}
        options={fetchedOptions}
        value={selectedOptions}
        inputValue={inputValue}
        onInputChange={(_, newVal, reason) => {
          if (reason !== 'reset') setInputValue(newVal);
        }}
        loading={isLoading}
        disabled={disabled}
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
            ) : chip;
          })
        }
        renderInput={(params) => (
          <TextField
            {...params}
            label={t('Payment Plan Purposes')}
            variant="outlined"
            size="small"
            required={required}
            error={!!error}
            data-cy="input-payment-plan-purposes"
          />
        )}
      />
      {error && <FormHelperText error>{error}</FormHelperText>}
    </>
  );
}
