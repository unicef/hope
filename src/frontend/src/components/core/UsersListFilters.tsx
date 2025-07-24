import { Grid2 as Grid, MenuItem } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { createHandleApplyFilterChange } from '@utils/utils';
import { FiltersSection } from './FiltersSection';
import { SearchTextField } from './SearchTextField';
import { SelectFilter } from './SelectFilter';
import { ReactElement } from 'react';

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
}: UsersListFiltersProps): ReactElement {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { businessArea } = useBaseUrl();

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

  const { data: choicesData, isLoading } = useQuery({
    queryKey: ['userChoices', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasUsersChoicesRetrieve({
        businessAreaSlug: businessArea,
      }),
  });

  if (isLoading || !choicesData) {
    return null;
  }

  const choices = {
    userPartnerChoices: choicesData.partnerChoicesTemp,
    userRolesChoices: choicesData.roleChoices,
    userStatusChoices: choicesData.statusChoices,
  };

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <Grid container spacing={3}>
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) => handleFilterChange('partner', e.target.value)}
            label={t('Partner')}
            value={filter.partner}
            data-cy="partner-filter"
          >
            {choices.userPartnerChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) => handleFilterChange('roles', e.target.value)}
            label={t('Role')}
            value={filter.roles}
            dataCy="role-filter"
          >
            {choices.userRolesChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {`${item.name} (${item.subsystem === 'CA' ? 'Cash Assist' : item.subsystem})`}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            label={t('Status')}
            value={filter.status}
            dataCy="status-filter"
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
