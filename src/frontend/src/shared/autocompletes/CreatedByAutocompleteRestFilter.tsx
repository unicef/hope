import { ReactElement, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useBusinessArea } from '@hooks/useBusinessArea';
import { useDebounce } from '@hooks/useDebounce';
import { useQuery } from '@tanstack/react-query';
import { PaginatedUserList } from '@restgenerated/models/PaginatedUserList';
import { RestService } from '@restgenerated/services/RestService';
import {
  createHandleApplyFilterChange,
  handleAutocompleteChange,
} from '@utils/utils';
import { BaseAutocompleteFilterRest } from './BaseAutocompleteFilterRest';

export const CreatedByAutocompleteRestFilter = ({
  disabled,
  name,
  filter,
  value,
  label,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  setFilter,
  additionalVariables,
}: {
  disabled?: boolean;
  name: string;
  filter: any;
  value: string;
  label?: string;
  initialFilter: any;
  appliedFilter: any;
  setAppliedFilter: (filter: any) => void;
  setFilter: (filter: any) => void;
  additionalVariables?: any;
}): ReactElement => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);
  const businessArea = useBusinessArea();

  const [queryVariables, setQueryVariables] = useState({
    limit: 100,
    businessAreaSlug: businessArea,
    search: debouncedInputText || undefined,
    ordering: 'first_name,last_name,email',
    ...additionalVariables,
  });

  const {
    data: userData,
    isLoading,
    refetch,
  } = useQuery<PaginatedUserList>({
    queryKey: ['businessAreasUsersList', queryVariables, businessArea],
    queryFn: () => RestService.restBusinessAreasUsersList(queryVariables),
  });

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

  const handleOptionSelected = (option: any, selectedValue: any) => {
    if (typeof selectedValue === 'string') {
      return option?.id === selectedValue;
    }
    return option?.id === selectedValue?.id;
  };

  const handleOptionLabel = (option: any) => {
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
      label={label || t('Created By')}
      dataCy="filters-created-by-autocomplete"
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
};
