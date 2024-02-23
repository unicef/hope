import { Grid, MenuItem } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useUserChoiceDataQuery } from '@generated/graphql';
import { createHandleApplyFilterChange } from '@utils/utils';
import { FiltersSection } from './FiltersSection';
import { SearchTextField } from './SearchTextField';
import { SelectFilter } from './SelectFilter';

interface UsersListFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

export function UsersListFilters({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: UsersListFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();

  const { handleFilterChange, applyFilterChanges, clearFilter } =
    createHandleApplyFilterChange(
      initialFilter,
      navigate,
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

  const { data: choices } = useUserChoiceDataQuery();
  if (!choices) {
    return null;
  }

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <Grid container spacing={3}>
        <Grid item xs={3}>
          <div style={{ position: 'relative', bottom: '8px', width: '100%' }}>
            <SearchTextField
              label={t('Search')}
              value={filter.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
            />
          </div>
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('partner', e.target.value)}
            label={t('Partner')}
            value={filter.partner}
          >
            {choices.userPartnerChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('roles', e.target.value)}
            label={t('Role')}
            value={filter.roles}
          >
            {choices.userRolesChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name} (
                {item.subsystem === 'CA' ? 'Cash Assist' : item.subsystem})
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            label={t('Status')}
            value={filter.status}
          >
            {choices.userStatusChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
