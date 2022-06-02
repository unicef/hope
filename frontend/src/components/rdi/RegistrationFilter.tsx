import { InputAdornment, MenuItem } from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import { KeyboardDatePicker } from '@material-ui/pickers';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import TextField from '../../shared/TextField';
import { useRegistrationChoicesQuery } from '../../__generated__/graphql';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { SelectFilter } from '../core/SelectFilter';
import { UsersAutocomplete } from '../core/UsersAutocomplete';

const StyledTextField = styled(TextField)`
  flex: 1;
  && {
    min-width: 150px;
  }
`;

interface RegistrationFiltersProps {
  onFilterChange;
  filter;
}
export function RegistrationFilters({
  onFilterChange,
  filter,
}: RegistrationFiltersProps): React.ReactElement {
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  const { t } = useTranslation();
  const { data: registrationChoicesData } = useRegistrationChoicesQuery();
  if (!registrationChoicesData) {
    return null;
  }

  return (
    <ContainerWithBorder>
      <StyledTextField
        variant='outlined'
        label={t('Search')}
        margin='dense'
        onChange={(e) => handleFilterChange(e, 'search')}
        value={filter.search}
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />
      <KeyboardDatePicker
        variant='inline'
        inputVariant='outlined'
        margin='dense'
        label={t('Import Date')}
        autoOk
        onChange={(date) => onFilterChange({ ...filter, importDate: date })}
        value={filter.importDate || null}
        format='YYYY-MM-DD'
        InputAdornmentProps={{ position: 'end' }}
      />
      <UsersAutocomplete
        onInputTextChange={(value) =>
          onFilterChange({ ...filter, userInputValue: value })
        }
        inputValue={filter.userInputValue}
        onChange={(e, option) => {
          if (!option) {
            onFilterChange({ ...filter, importedBy: undefined });
            return;
          }
          onFilterChange({ ...filter, importedBy: option.node.id });
        }}
        value={filter.importedBy}
      />

      <SelectFilter
        value={filter.status || ''}
        label={t('Status')}
        onChange={(e) => handleFilterChange(e, 'status')}
      >
        <MenuItem value=''>
          <em>{t('None')}</em>
        </MenuItem>
        {registrationChoicesData.registrationDataStatusChoices.map((item) => {
          return (
            <MenuItem key={item.value} value={item.value}>
              {item.name}
            </MenuItem>
          );
        })}
      </SelectFilter>
    </ContainerWithBorder>
  );
}
