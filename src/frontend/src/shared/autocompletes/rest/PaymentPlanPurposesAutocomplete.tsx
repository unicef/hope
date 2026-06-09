import { useBaseUrl } from '@hooks/useBaseUrl';
import { useDebounce } from '@hooks/useDebounce';
import { FormikChipAutocomplete } from '@shared/Formik/FormikChipAutocomplete/FormikChipAutocomplete';
import { PaginatedPaymentPlanPurposeList } from '@restgenerated/models/PaginatedPaymentPlanPurposeList';
import { RestService } from '@restgenerated/services/RestService';
import { FieldInputProps, FormikProps } from 'formik';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

interface Choice {
  value: string;
  name: string;
}

interface PaymentPlanPurposesAutocompleteProps {
  field: FieldInputProps<string[]>;
  form: FormikProps<unknown>;
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
      RestService.restBusinessAreasPaymentPlanPurposesList({
        businessAreaSlug: businessArea,
        search: debouncedSearch || undefined,
      }),
    select: (data: PaginatedPaymentPlanPurposeList): Choice[] =>
      (data?.results ?? []).map((p) => ({ value: p.id, name: p.name })),
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

  return (
    <FormikChipAutocomplete
      field={field}
      form={form}
      label={t('Payment Plan Purposes')}
      choices={knownOptions}
      options={fetchedOptions}
      lockedValues={lockedValues}
      disabled={disabled}
      required={required}
      loading={isLoading}
      inputValue={inputValue}
      onInputChange={setInputValue}
      serverSide
      data-cy="input-payment-plan-purposes"
    />
  );
}
