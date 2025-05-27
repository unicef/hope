import { useBaseUrl } from '@hooks/useBaseUrl';
import { useDebounce } from '@hooks/useDebounce';
import { PaginatedTargetPopulationListList } from '@restgenerated/models/PaginatedTargetPopulationListList';
import { RestService } from '@restgenerated/services/RestService';
import {
  createHandleApplyFilterChange,
  handleAutocompleteChange,
} from '@utils/utils';
import React, { ReactElement, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { BaseAutocompleteFilterRest } from '../BaseAutocompleteFilterRest';

export const TargetPopulationAutocompleteRestFilter = ({
  value,
  name,
  filter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  setFilter,
  disabled,
  dataCy = 'filters-target-population-autocomplete',
  onChange, // Added onChange prop
}: {
  value?: any;
  name?: string;
  filter?: any;
  initialFilter?: any;
  appliedFilter?: any;
  setAppliedFilter?: (filter: any) => void;
  setFilter?: (filter: any) => void;
  disabled?: boolean;
  dataCy?: string;
  onChange?: (value: any) => void; // Added onChange prop type
}): ReactElement => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);

  // Query parameters for target populations
  const [queryVariables, setQueryVariables] = useState({
    name: debouncedInputText || undefined,
    limit: 20,
  });

  // Update query variables when search text changes
  useEffect(() => {
    setQueryVariables((prev) => ({
      ...prev,
      name: debouncedInputText || undefined,
    }));
  }, [debouncedInputText]);

  // Use the RestService function to fetch target population data
  const {
    data: targetPopulationData,
    isLoading,
    refetch,
  } = useQuery<PaginatedTargetPopulationListList>({
    queryKey: ['targetPopulations', businessArea, programId, queryVariables],
    queryFn: () =>
      RestService.restBusinessAreasProgramsTargetPopulationsList({
        businessAreaSlug: businessArea || '',
        programSlug: programId || '',
        ...queryVariables,
      }),
    enabled: !!businessArea && !!programId,
  });

  const loadData = useCallback(() => {
    if (businessArea && programId) {
      refetch();
    }
  }, [businessArea, programId, refetch]);

  // Create handleFilterChange only if filter-related props are provided
  const { handleFilterChange } =
    initialFilter && setFilter && appliedFilter && setAppliedFilter
      ? createHandleApplyFilterChange(
          initialFilter,
          navigate,
          location,
          filter,
          setFilter,
          appliedFilter,
          setAppliedFilter,
        )
      : { handleFilterChange: undefined };

  // Process and map target population data
  const options = targetPopulationData?.results
    ? targetPopulationData.results.map((item) => ({
        name: item.name || '',
        value: item.id,
      }))
    : [];

  // Handle change events for both filter and direct onChange patterns
  const handleChangeWrapper = (_, selectedValue) => {
    if (handleFilterChange && name) {
      handleAutocompleteChange(name, selectedValue?.value, handleFilterChange);
    }
    // Call onChange prop if provided
    if (onChange) {
      onChange(selectedValue?.value);
    }
  };

  return (
    <BaseAutocompleteFilterRest
      value={value || ''}
      disabled={disabled}
      label={t('Target Population')}
      dataCy={dataCy}
      loadData={loadData}
      loading={isLoading}
      options={options}
      handleChange={handleChangeWrapper}
      handleOpen={() => setOpen(true)}
      open={open}
      handleClose={(_, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        setInputValue('');
      }}
      handleOptionSelected={(option, selectedValue) =>
        typeof selectedValue === 'string'
          ? option?.value === selectedValue
          : option?.value === selectedValue?.value
      }
      handleOptionLabel={(option) => {
        if (typeof option === 'string') {
          const matchingOption = options.find((item) => item.value === option);
          return matchingOption ? matchingOption.name : option;
        }
        return option?.name || '';
      }}
      data={targetPopulationData}
      inputValue={inputValue}
      onInputTextChange={setInputValue}
      debouncedInputText={debouncedInputText}
    />
  );
};
