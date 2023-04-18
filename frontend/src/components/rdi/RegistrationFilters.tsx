import { InputAdornment, MenuItem } from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import moment from 'moment';
import React from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import TextField from '../../shared/TextField';
import { useRegistrationChoicesQuery } from '../../__generated__/graphql';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { DatePickerFilter } from '../core/DatePickerFilter';
import { SelectFilter } from '../core/SelectFilter';
import { AssigneeAutocomplete } from '../../shared/AssigneeAutocomplete/AssigneeAutocomplete';
import { createHandleFilterChange } from '../../utils/utils';
import { SearchTextField } from '../core/SearchTextField';

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
export const RegistrationFilters = ({
  onFilterChange,
  filter,
}: RegistrationFiltersProps): React.ReactElement => {
  const history = useHistory();
  const location = useLocation();

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );

  const { t } = useTranslation();
  const { data: registrationChoicesData } = useRegistrationChoicesQuery();
  if (!registrationChoicesData) {
    return null;
  }

  return (
    <ContainerWithBorder>
      <SearchTextField
        label={t('Search')}
        value={filter.search}
        onChange={(e) => handleFilterChange('search', e.target.value)}
        data-cy='filter-search'
      />
      <DatePickerFilter
        label={t('Import Date')}
        onChange={(date) =>
          handleFilterChange('importDate', moment(date).format('YYYY-MM-DD'))
        }
        value={filter.importDate}
        data-cy='filter-import-date'
      />
      <AssigneeAutocomplete
        name='importedBy'
        value={filter.importedBy}
        onFilterChange={onFilterChange}
        filter={filter}
        label={t('Imported By')}
        data-cy='filter-imported-by'
      />
      <SelectFilter
        value={filter.status}
        label={t('Status')}
        onChange={(e) => handleFilterChange('status', e.target.value)}
        data-cy='filter-status'
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
};
