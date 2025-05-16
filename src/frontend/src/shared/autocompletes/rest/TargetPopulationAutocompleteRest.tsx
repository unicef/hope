import { fetchTargetPopulations } from '@api/targetPopulationApi';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  handleOptionSelected,
  createHandleApplyFilterChange,
  handleAutocompleteChange,
} from '@utils/utils';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { BaseAutocompleteRest } from './BaseAutocompleteRest';

export const TargetPopulationAutocompleteRest = ({
  value,
  onChange,
  name,
  filter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  setFilter,
  disabled,
}: {
  value?: any;
  onChange?: (e: any) => void;
  name?: string;
  filter?: any;
  initialFilter?: any;
  appliedFilter?: any;
  setAppliedFilter?: (filter: any) => void;
  setFilter?: (filter: any) => void;
  disabled?: boolean;
}): ReactElement => {
  const { t } = useTranslation();
  const [queryParams, setQueryParams] = useState({});
  const { businessArea, programId } = useBaseUrl();
  const navigate = useNavigate();
  const location = useLocation();

  // Define the mapOptions function
  const mapOptions = (options) => {
    return options.map((option) => ({
      name: option.name,
      value: option.id,
    }));
  };

  // Create handleFilterChange only if filter-related props are provided
  const handleFilterChange =
    initialFilter && setFilter && appliedFilter && setAppliedFilter
      ? createHandleApplyFilterChange(
          initialFilter,
          navigate,
          location,
          filter,
          setFilter,
          appliedFilter,
          setAppliedFilter,
        ).handleFilterChange
      : undefined;

  // Handler for change events that supports both patterns
  const handleChangeWrapper = (_, selectedValue) => {
    if (onChange) {
      // Direct onChange pattern
      onChange(selectedValue);
    } else if (handleFilterChange && name) {
      // Filter-based pattern
      handleAutocompleteChange(name, selectedValue?.value, handleFilterChange);
    }
  };

  return (
    <BaseAutocompleteRest
      value={value}
      disabled={disabled}
      label={t('Target Population')}
      dataCy="filters-target-population-autocomplete"
      fetchFunction={fetchTargetPopulations}
      businessArea={businessArea}
      programId={programId}
      handleChange={handleChangeWrapper}
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
