import { ReactElement, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useDebounce } from '@hooks/useDebounce';
import { useQuery } from '@tanstack/react-query';
import { PaginatedRegistrationDataImportListList } from '@restgenerated/models/PaginatedRegistrationDataImportListList';
import { RestService } from '@restgenerated/services/RestService';
import {
  createHandleApplyFilterChange,
  handleAutocompleteChange,
} from '@utils/utils';
import { BaseAutocompleteFilterRest } from './BaseAutocompleteFilterRest';

export function RdiAutocompleteRestFilter({
  disabled,
  name,
  filter,
  value,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  setFilter,
  programSlug,
  onChange,
}: {
  disabled?: boolean;
  name?: string;
  filter?: any;
  value?: string;
  initialFilter?: any;
  appliedFilter?: any;
  setAppliedFilter?: (filter: any) => void;
  setFilter?: (filter: any) => void;
  programSlug?: string;
  onChange?: (selectedItem: string | null) => void;
}): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const [inputValue, setInputValue] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);
  const { businessArea, programId } = useBaseUrl();

  // Use provided programSlug or fall back to programId from the route
  const effectiveProgramSlug = programSlug || programId;

  const [queryVariables, setQueryVariables] = useState({
    limit: 20,
    businessAreaSlug: businessArea,
    programSlug: effectiveProgramSlug || '',
    search: debouncedInputText || undefined,
    ordering: 'name',
  });

  const {
    data: rdiData,
    isLoading,
    refetch,
  } = useQuery<PaginatedRegistrationDataImportListList>({
    queryKey: [
      'businessAreasProgramsRegistrationDataImportsList',
      queryVariables,
      businessArea,
      effectiveProgramSlug,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsRegistrationDataImportsList(
        queryVariables,
      ),
    enabled: !!effectiveProgramSlug && !!businessArea,
  });

  useEffect(() => {
    setQueryVariables((prev) => ({
      ...prev,
      search: debouncedInputText || undefined,
    }));
  }, [debouncedInputText]);

  // Update program slug in queryVariables when it changes
  useEffect(() => {
    setQueryVariables((prev) => ({
      ...prev,
      programSlug: effectiveProgramSlug || '',
    }));
  }, [effectiveProgramSlug]);

  const loadData = useCallback(() => {
    if (businessArea && effectiveProgramSlug) {
      refetch();
    }
  }, [businessArea, effectiveProgramSlug, refetch]);

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

  const registrationDataImports = rdiData?.results || [];
  const options = registrationDataImports.map((rdi) => ({
    id: rdi.id,
    name: rdi.name,
  }));

  const handleOptionSelected = (option: any, selectedValue: any) => {
    if (typeof selectedValue === 'string') {
      return option?.id === selectedValue;
    }
    return option?.id === selectedValue?.id;
  };

  const handleOptionLabel = (option: any) => {
    if (typeof option === 'string') {
      const matchingRdi = registrationDataImports.find(
        (rdi) => rdi.id === option,
      );
      return matchingRdi ? matchingRdi.name : option;
    }
    return option?.name || '';
  };

  const onInputTextChange = (v: string) => {
    setInputValue(v);
  };

  return (
    <BaseAutocompleteFilterRest
      value={value}
      disabled={disabled}
      label={t('Registration Data Import')}
      dataCy="filters-registration-data-import"
      loadData={loadData}
      loading={isLoading}
      options={options}
      handleChange={(_, selectedValue) => {
        if (!selectedValue) {
          onInputTextChange('');
        }
        if (onChange) {
          onChange(selectedValue?.id || null);
        } else if (handleFilterChange && name) {
          handleAutocompleteChange(name, selectedValue?.id, handleFilterChange);
        }
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
      data={rdiData}
      inputValue={inputValue}
      onInputTextChange={onInputTextChange}
      debouncedInputText={debouncedInputText}
    />
  );
}
