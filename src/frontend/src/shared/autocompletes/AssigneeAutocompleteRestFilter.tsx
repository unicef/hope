import type { Filter } from '@utils/utils';
import {
  createHandleApplyFilterChange,
  handleAutocompleteChange,
} from '@utils/utils';
import type { ReactElement } from 'react';
import { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useDebounce } from '@hooks/useDebounce';
import { useQuery } from '@tanstack/react-query';
import type { PaginatedUserList } from '@restgenerated/models/PaginatedUserList';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { BaseAutocompleteFilterRest } from './BaseAutocompleteFilterRest';
import type { AutocompleteOption } from './types';

export function AssigneeAutocompleteRestFilter({
  disabled,
  name,
  filter,
  value,
  label,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  setFilter,
  dataCy = 'assignee-autocomplete',
}: {
  disabled?: boolean;
  name: string;
  filter: Filter;
  value: string;
  label: string;
  initialFilter: Filter;
  appliedFilter: Filter;
  setAppliedFilter: (filter: Filter) => void;
  setFilter: (filter: Filter) => void;
  dataCy?: string;
}): ReactElement {
  const { businessArea } = useBaseUrl();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const [inputValue, setInputValue] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);

  const [queryVariables, setQueryVariables] = useState({
    limit: 20,
    businessAreaSlug: businessArea,
    search: debouncedInputText || undefined,
    ordering: 'first_name,last_name,email',
  });

  const {
    data: userData,
    isLoading,
    refetch,
  } = useQuery<PaginatedUserList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasUsersList,
      queryVariables,
    ),
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

  const users = userData?.results || [];
  const options = users.map((user) => ({
    id: user.id,
    name: `${user.firstName} ${user.lastName}`.trim() || user.email,
  }));

  // Both sides arrive as `AutocompleteOption | string`: MUI hands back the raw
  // input text before an option is picked. Comparing without narrowing
  // `option` reads `.id` off a string and silently never matches.
  const handleOptionSelected = (
    option: AutocompleteOption | string,
    selectedValue: AutocompleteOption | string,
  ) => {
    const optionKey = typeof option === 'string' ? option : option?.id;
    const valueKey =
      typeof selectedValue === 'string' ? selectedValue : selectedValue?.id;
    return optionKey === valueKey;
  };

  const handleOptionLabel = (option: AutocompleteOption | string) => {
    if (typeof option === 'string') {
      const matchingUser = users.find((user) => user.id === option);
      return matchingUser
        ? `${matchingUser.firstName || ''} ${matchingUser.lastName || ''}`.trim() ||
            matchingUser.email
        : option;
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
      label={label}
      dataCy={dataCy}
      loadData={loadData}
      loading={isLoading}
      options={options}
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
      data={userData}
      inputValue={inputValue}
      onInputTextChange={onInputTextChange}
      debouncedInputText={debouncedInputText}
    />
  );
}
