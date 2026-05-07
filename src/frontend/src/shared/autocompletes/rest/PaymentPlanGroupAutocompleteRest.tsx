import { useBaseUrl } from '@hooks/useBaseUrl';
import { handleOptionSelected } from '@utils/utils';
import { ReactElement, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { BaseAutocompleteRest } from './BaseAutocompleteRest';
import { RestService } from '@restgenerated/services/RestService';

export const PaymentPlanGroupAutocompleteRest = ({
  value,
  onChange,
  required = false,
  error = null,
  cycleId,
}: {
  value;
  onChange: (e) => void;
  required?: boolean;
  error?: string;
  cycleId?: string;
}): ReactElement => {
  const { t } = useTranslation();
  const [queryParams, setQueryParams] = useState({
    offset: 0,
    limit: 100,
    ordering: 'name',
    cycle: cycleId,
  });
  const { businessArea, programId } = useBaseUrl();

  useEffect(() => {
    setQueryParams((prev) => ({ ...prev, cycle: cycleId }));
  }, [cycleId]);

  const mapOptions = (options) => {
    return options.map((option) => ({
      name: option.name,
      value: option.id,
    }));
  };

  return (
    <BaseAutocompleteRest
      value={value}
      label={t('Payment Plan Group')}
      dataCy="filters-payment-plan-group-autocomplete"
      fetchFunction={(_, __, params) =>
        RestService.restBusinessAreasProgramsPaymentPlanGroupsList({
          businessAreaSlug: businessArea,
          programCode: programId,
          ...params,
        })
      }
      businessArea={businessArea}
      programId={programId}
      handleChange={(_, selectedValue) => {
        onChange(selectedValue);
      }}
      handleOptionSelected={(option, value1) =>
        handleOptionSelected(option?.value, value1)
      }
      handleOptionLabel={(option) => {
        return option === '' ? '' : option.name;
      }}
      onDebouncedInputTextChanges={(text) => {
        setQueryParams((oldQueryParams) => ({
          ...oldQueryParams,
          name: text,
        }));
      }}
      startAdornment={null}
      mapOptions={mapOptions}
      queryParams={queryParams}
      required={required}
      error={error}
    />
  );
};
