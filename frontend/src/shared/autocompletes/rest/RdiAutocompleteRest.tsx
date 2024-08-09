import { fetchRegistrationDataImports } from '@api/rdiApi';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { handleOptionSelected } from '@utils/utils';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { BaseAutocompleteRest } from './BaseAutocompleteRest';

export const RdiAutocompleteRest = ({
  disabled,
  value,
  onChange,
}: {
  disabled?;
  value?: string;
  onChange: (e) => void;
}): React.ReactElement => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const [queryParams, setQueryParams] = useState({});
  const mapOptions = (options) => {
    return options.map((option) => ({
      name: option.name,
      value: option.id,
    }));
  };
  return (
    <BaseAutocompleteRest
      value={value}
      disabled={disabled}
      label={t('Registration Data Import')}
      dataCy="filters-registration-data-import"
      fetchFunction={fetchRegistrationDataImports}
      businessArea={businessArea}
      programId={programId}
      queryParams={queryParams}
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
          status: 'MERGED',
          name: text,
        });
      }}
      startAdornment={null}
      mapOptions={mapOptions}
    />
  );
};
