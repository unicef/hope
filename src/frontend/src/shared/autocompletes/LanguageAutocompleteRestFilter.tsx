import { ReactElement, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useDebounce } from '@hooks/useDebounce';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import {
  createHandleApplyFilterChange,
  handleAutocompleteChange,
} from '@utils/utils';
import { BaseAutocompleteFilterRest } from './BaseAutocompleteFilterRest';

export function LanguageAutocompleteRestFilter({
  disabled,
  name,
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
  filter?: any;
  value?: string;
  initialFilter: any;
  appliedFilter: any;
  setAppliedFilter: (filter: any) => void;
  setFilter: (filter: any) => void;
  dataCy?: string;
}): ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const [inputValue, setInputValue] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);

  // TODO: Replace with dedicated language endpoint when available
  // This is a temporary placeholder using the users endpoint
  const [queryVariables, setQueryVariables] = useState({
    limit: 20,
    businessAreaSlug: businessArea,
    search: debouncedInputText || undefined,
  });

  const {
    data: languageData,
    isLoading,
    refetch,
  } = useQuery({
    // TODO: Replace with appropriate language endpoint query key and function
    queryKey: ['temporaryLanguagesList', queryVariables, businessArea],
    queryFn: () => RestService.restBusinessAreasUsersList(queryVariables),
  });

  // Update query variables when search text changes
  useEffect(() => {
    setQueryVariables((prev) => ({
      ...prev,
      search: debouncedInputText || undefined,
    }));
  }, [debouncedInputText]);

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

  // TODO: Replace with proper language data mapping when endpoint is available
  // This is a mock structure to simulate language data from the users endpoint
  const languages = languageData?.results || [];
  const options = languages.map((user) => ({
    id: user.id,
    code: user.id, // Using ID as code temporarily
    name: user.firstName || user.email || 'Unknown Language',
  }));

  const handleOptionSelected = (option: any, selectedValue: any) => {
    if (typeof selectedValue === 'string') {
      return option?.code === selectedValue;
    }
    return option?.code === selectedValue?.code;
  };

  const handleOptionLabel = (option: any) => {
    if (typeof option === 'string') {
      const matchingLanguage = options.find((lang) => lang.code === option);
      return matchingLanguage ? matchingLanguage.name : option;
    }
    return option?.name || '';
  };

  return (
    <BaseAutocompleteFilterRest
      value={value || ''}
      disabled={disabled}
      label={t('Preferred language')}
      dataCy={dataCy}
      loadData={loadData}
      loading={isLoading}
      options={options}
      handleChange={(_, selectedValue) => {
        if (!selectedValue) {
          setInputValue('');
        }
        handleAutocompleteChange(name, selectedValue?.code, handleFilterChange);
      }}
      handleOpen={() => setOpen(true)}
      open={open}
      handleClose={(_, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        setInputValue('');
      }}
      handleOptionSelected={handleOptionSelected}
      handleOptionLabel={handleOptionLabel}
      data={languageData}
      inputValue={inputValue}
      onInputTextChange={setInputValue}
      debouncedInputText={debouncedInputText}
    />
  );
}
