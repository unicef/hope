import { Grid, MenuItem } from '@material-ui/core';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { useRegistrationChoicesQuery } from '../../__generated__/graphql';
import { AssigneeAutocomplete } from '../../shared/AssigneeAutocomplete/AssigneeAutocomplete';
import { createHandleApplyFilterChange } from '../../utils/utils';
import { ClearApplyButtons } from '../core/ClearApplyButtons';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { DatePickerFilter } from '../core/DatePickerFilter';
import { SearchTextField } from '../core/SearchTextField';
import { SelectFilter } from '../core/SelectFilter';

interface RegistrationFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const RegistrationFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: RegistrationFiltersProps): React.ReactElement => {
  const history = useHistory();
  const location = useLocation();

  const {
    handleFilterChange,
    applyFilterChanges,
    clearFilter,
  } = createHandleApplyFilterChange(
    initialFilter,
    history,
    location,
    filter,
    setFilter,
    appliedFilter,
    setAppliedFilter,
  );
  const handleApplyFilter = (): void => {
    applyFilterChanges();
  };

  const handleClearFilter = (): void => {
    clearFilter();
  };

  const { t } = useTranslation();
  const { data: registrationChoicesData } = useRegistrationChoicesQuery();
  if (!registrationChoicesData) {
    return null;
  }

  return (
    <ContainerWithBorder>
      <Grid container spacing={3} alignItems='flex-end'>
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy='filter-search'
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            label={t('Import Date')}
            onChange={(date) =>
              handleFilterChange(
                'importDate',
                moment(date).format('YYYY-MM-DD'),
              )
            }
            value={filter.importDate}
            data-cy='filter-import-date'
          />
        </Grid>
        <Grid item xs={3}>
          <AssigneeAutocomplete
            name='importedBy'
            value={filter.importedBy}
            onFilterChange={setFilter}
            filter={filter}
            label={t('Imported By')}
            data-cy='filter-imported-by'
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            value={filter.status}
            label={t('Status')}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            data-cy='filter-status'
          >
            <MenuItem value=''>
              <em>{t('None')}</em>
            </MenuItem>
            {registrationChoicesData.registrationDataStatusChoices.map(
              (item) => {
                return (
                  <MenuItem key={item.value} value={item.value}>
                    {item.name}
                  </MenuItem>
                );
              },
            )}
          </SelectFilter>
        </Grid>
      </Grid>
      <ClearApplyButtons
        clearHandler={handleClearFilter}
        applyHandler={handleApplyFilter}
      />
    </ContainerWithBorder>
  );
};
