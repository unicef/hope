import { ReactElement, useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useDebounce } from '@hooks/useDebounce';
import { useQuery } from '@tanstack/react-query';
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
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const [inputValue, setInputValue] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);

  const {
    data: languageData,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ['languagesList'],
    queryFn: () => RestService.restChoicesLanguagesList(),
  });

  const loadData = useCallback(() => {
    refetch();
  }, [refetch]);

  const { handleFilterChange } = createHandleApplyFilterChange(
    initialFilter,
    navigate,
    location,
    filter,
    setFilter,
    appliedFilter,
    setAppliedFilter,
  );

  // Map languages data to options format and filter based on input
  const languages = languageData || [];
  const filteredLanguages = languages.filter((lang) =>
    lang.name.toLowerCase().includes(debouncedInputText.toLowerCase()),
  );

  const options = filteredLanguages.map((lang) => ({
    id: lang.value,
    code: lang.value,
    name: lang.name,
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
