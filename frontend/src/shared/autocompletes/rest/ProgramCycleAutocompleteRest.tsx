import { useBaseUrl } from '@hooks/useBaseUrl';
import { handleOptionSelected } from '@utils/utils';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { BaseAutocompleteRest } from './BaseAutocompleteRest';
import { fetchProgramCycles, ProgramCyclesQuery } from '@api/programCycleApi';

export const ProgramCycleAutocompleteRest = ({
  value,
  onChange,
}: {
  value;
  onChange: (e) => void;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [queryParams, setQueryParams] = useState<ProgramCyclesQuery>({
    offset: 0,
    limit: 10,
    ordering: 'title',
  });
  const { businessArea, programId } = useBaseUrl();

  // Define the mapOptions function
  const mapOptions = (options) => {
    return options.map((option) => ({
      name: option.title,
      value: option.id,
    }));
  };
  return (
    <BaseAutocompleteRest
      value={value}
      label={t('Programme Cycle')}
      dataCy="filters-program-cycle-autocomplete"
      fetchFunction={fetchProgramCycles}
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
          title: text,
        }));
      }}
      startAdornment={null}
      mapOptions={mapOptions}
      queryParams={queryParams}
    />
  );
};
