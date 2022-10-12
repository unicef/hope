import { Box, InputAdornment, MenuItem } from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import TextField from '../../shared/TextField';
import { useRegistrationChoicesQuery } from '../../__generated__/graphql';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { DatePickerFilter } from '../core/DatePickerFilter';
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
  addBorder?: boolean;
}
export function RegistrationFilters({
  onFilterChange,
  filter,
  addBorder = true,
}: RegistrationFiltersProps): React.ReactElement {
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  const { t } = useTranslation();
  const { data: registrationChoicesData } = useRegistrationChoicesQuery();
  if (!registrationChoicesData) {
    return null;
  }

  const renderTable = (): React.ReactElement => {
    return (
      <Box display="flex" alignItems="center">
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
        <DatePickerFilter
          label={t('Import Date')}
          onChange={(date) => onFilterChange({ ...filter, importDate: date })}
          value={filter.importDate}
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
      </Box>
    );
  };

  return addBorder ? (
    <ContainerWithBorder>{renderTable()}</ContainerWithBorder>
  ) : (
    renderTable()
  );
}
