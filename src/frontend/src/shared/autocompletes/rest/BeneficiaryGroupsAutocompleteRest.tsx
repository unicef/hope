import { useBaseUrl } from '@hooks/useBaseUrl';
import { handleOptionSelected } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { BaseAutocompleteRest } from './BaseAutocompleteRest';
import { fetchBeneficiaryGroups } from '@api/programsApi';

export const BeneficiaryGroupAutocompleteRest = ({
  value,
  onChange,
  required = false,
  error = null,
}: {
  value;
  onChange: (e) => void;
  required?: boolean;
  error?: string;
}): ReactElement => {
  const { t } = useTranslation();
  const [queryParams, setQueryParams] = useState({
    offset: 0,
    limit: 10,
    ordering: 'name',
  });
  const { businessArea, programId } = useBaseUrl();

  // Define the mapOptions function
  const mapOptions = (options) => {
    return options.map((option) => ({
      name: option.name,
      value: option.id,
    }));
  };

  return (
    <BaseAutocompleteRest
      programId={programId}
      value={value}
      label={t('Beneficiary Group')}
      dataCy="filters-beneficiary-group-autocomplete"
      fetchFunction={fetchBeneficiaryGroups}
      businessArea={businessArea}
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
