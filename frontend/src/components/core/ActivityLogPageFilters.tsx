import { Grid, MenuItem } from '@material-ui/core';
import ViewModuleRoundedIcon from '@material-ui/icons/ViewModuleRounded';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { AssigneeAutocomplete } from '../../shared/AssigneeAutocomplete';
import { createHandleApplyFilterChange } from '../../utils/utils';
import { ClearApplyButtons } from './ClearApplyButtons';
import { ContainerWithBorder } from './ContainerWithBorder';
import { SearchTextField } from './SearchTextField';
import { SelectFilter } from './SelectFilter';

interface ActivityLogPageFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export function ActivityLogPageFilters({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: ActivityLogPageFiltersProps): React.ReactElement {
  const { t } = useTranslation();
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

  const modules = {
    program: 'Programme',
    household: 'Household',
    individual: 'Individual',
    grievanceticket: 'Grievance ticket',
    paymentverificationplan: 'Cash plan payment verification',
    targetpopulation: 'Target Population',
    registrationdataimport: 'Registration data import',
  };
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('module', e.target.value)}
            label={t('Module')}
            value={filter.module}
            icon={<ViewModuleRoundedIcon />}
            SelectDisplayProps={{
              'data-cy': 'filters-residence-status',
            }}
            MenuProps={{
              'data-cy': 'filters-residence-status-options',
            }}
          >
            <MenuItem value=''>
              <em>{t('None')}</em>
            </MenuItem>
            {Object.entries(modules)
              .sort()
              .map(([key, value]) => (
                <MenuItem key={key} value={key}>
                  {value}
                </MenuItem>
              ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <AssigneeAutocomplete
            label='User'
            filter={filter}
            name='userId'
            value={filter.userId}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </Grid>
      </Grid>
      <ClearApplyButtons
        clearHandler={handleClearFilter}
        applyHandler={handleApplyFilter}
      />
    </ContainerWithBorder>
  );
}
