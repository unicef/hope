import { fetchTargetPopulations } from '@api/targetPopulationApi';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useDebounce } from '@hooks/useDebounce';
import { handleAutocompleteClose, handleOptionSelected } from '@utils/utils';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { BaseAutocompleteRest } from './BaseAutocompleteRest';

export const TargetPopulationAutocompleteRest = ({
  value,
  onChange,
}: {
  value;
  onChange: (e) => void;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [queryParams, setQueryParams] = useState({});
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
      value={value}
      label={t('Target Population')}
      dataCy="filters-target-population-autocomplete"
      fetchFunction={fetchTargetPopulations}
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
        setQueryParams({
          name: text,
        });
      }}
      startAdornment={null}
      mapOptions={mapOptions}
      queryParams={queryParams}
    />
  );
};
