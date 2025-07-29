import { ReactElement, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useDebounce } from '@hooks/useDebounce';
import {
  createHandleApplyFilterChange,
  handleAutocompleteChange,
} from '@utils/utils';
import { BaseAutocomplete } from './BaseAutocomplete';

export function AdminAreaAutocomplete({
  disabled,
  name,
  level,
  filter,
  value,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  setFilter,
  dataCy,
}: {
  disabled?: boolean;
  name: string;
  level: number;
  filter;
  value: string;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  setFilter: (filter) => void;
  dataCy?: string;
}): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);
  const navigate = useNavigate();
  const location = useLocation();
  const { businessArea } = useBaseUrl();

  const [queryVariables, setQueryVariables] = useState({
    limit: 20,
    areaTypeAreaLevel: level,
    search: debouncedInputText || undefined,
  });

  useEffect(() => {
    setQueryVariables((prev) => ({
      ...prev,
      search: debouncedInputText || undefined,
      areaTypeAreaLevel: level,
    }));
  }, [debouncedInputText, level]);

  const {
    data: areasData,
    isLoading: loading,
    refetch,
  } = useQuery({
    queryKey: ['adminAreas', queryVariables, businessArea],
    queryFn: () =>
      RestService.restAreasList({
        ...queryVariables,
        // businessAreaSlug: businessArea, // Uncomment if needed by API
      }),
    enabled: open && !!businessArea,
    staleTime: 0,
    refetchOnWindowFocus: false,
  });

  const loadData = useCallback(() => {
    if (businessArea) {
      refetch();
    }
  }, [businessArea, refetch]);

  const { handleFilterChange } = createHandleApplyFilterChange(
    initialFilter,
    navigate,
    location,
    filter,
    setFilter,
    appliedFilter,
    setAppliedFilter,
  );

  const allEdges = areasData?.results || [];

  const handleOptionSelected = (option: any, selectedValue: any) => {
    if (typeof selectedValue === 'string') {
      return option?.id === selectedValue;
    }
    return option?.id === selectedValue?.id;
  };

  const handleOptionLabel = (option: any) => {
    if (typeof option === 'string') {
      const matching = allEdges.find((a) => a.id === option);
      return matching ? matching.name : option;
    }
    return option?.name || '';
  };

  const onInputTextChange = (v: string) => {
    setInputValue(v);
  };

  return (
    <BaseAutocomplete
      value={value}
      disabled={disabled}
      label={t(`Admin Level ${level}`)}
      dataCy={dataCy}
      loadData={loadData}
      loading={loading}
      allEdges={allEdges}
      handleChange={(_, selectedValue) => {
        if (!selectedValue) {
          onInputTextChange('');
        }
        handleAutocompleteChange(name, selectedValue?.id, handleFilterChange);
      }}
      handleOpen={() => setOpen(true)}
      open={open}
      handleClose={(_, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        onInputTextChange('');
      }}
      handleOptionSelected={handleOptionSelected}
      handleOptionLabel={handleOptionLabel}
      data={areasData}
      inputValue={inputValue}
      onInputTextChange={onInputTextChange}
      debouncedInputText={debouncedInputText}
    />
  );
}
