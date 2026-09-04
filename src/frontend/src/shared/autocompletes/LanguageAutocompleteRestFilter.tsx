import { ReactElement, useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useDebounce } from '@hooks/useDebounce';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import {
  createHandleApplyFilterChange,
  Filter,
  handleAutocompleteChange,
} from '@utils/utils';
import { BaseAutocompleteFilterRest } from './BaseAutocompleteFilterRest';
import { AutocompleteOption } from './types';

type LanguageOption = AutocompleteOption & { code: string };

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
  filter?: Filter;
  value?: string;
  initialFilter: Filter;
  appliedFilter: Filter;
  setAppliedFilter: (filter: Filter) => void;
  setFilter: (filter: Filter) => void;
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
    queryKey: restQueryKey(RestService.restChoicesLanguagesList),
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
  ); // Map languages data to options format and filter based on input
  const languages = languageData || [];
  const filteredLanguages = languages.filter((lang) =>
    lang.name.toLowerCase().includes(debouncedInputText.toLowerCase()),
  );

  const options = filteredLanguages.map((lang) => ({
    id: lang.value,
    code: lang.value,
    name: lang.name,
  }));

  // Both sides arrive as `LanguageOption | string`: MUI hands back the raw
  // input text before an option is picked. Comparing without narrowing
  // `option` reads `.code` off a string and silently never matches.
  const handleOptionSelected = (
    option: LanguageOption | string,
    selectedValue: LanguageOption | string,
  ) => {
    const optionKey = typeof option === 'string' ? option : option?.code;
    const valueKey =
      typeof selectedValue === 'string' ? selectedValue : selectedValue?.code;
    return optionKey === valueKey;
  };

  const handleOptionLabel = (option: LanguageOption | string) => {
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
