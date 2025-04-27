import { useBaseUrl } from '@hooks/useBaseUrl';
import { handleOptionSelected } from '@utils/utils';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { BaseAutocompleteRest } from './BaseAutocompleteRest';
import { RestService } from '@restgenerated/services/RestService';

export const ProgramCycleAutocompleteRest = ({
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
    ordering: 'title',
    status: ['ACTIVE', 'DRAFT'],
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
      fetchFunction={() =>
        RestService.restBusinessAreasProgramsCyclesList({
          businessAreaSlug: businessArea,
          programSlug: programId,
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
          title: text,
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
