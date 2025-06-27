import { Grid2 as Grid, MenuItem } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { GrievancesChoiceDataQuery } from '@generated/graphql';
import { AdminAreaAutocomplete } from '@shared/autocompletes/AdminAreaAutocomplete';
import { createHandleApplyFilterChange } from '@utils/utils';
import { DatePickerFilter } from '@core/DatePickerFilter';
import { FiltersSection } from '@core/FiltersSection';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { ReactElement } from 'react';

interface LookUpLinkedTicketsFiltersProps {
  filter;
  choicesData: GrievancesChoiceDataQuery;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export function LookUpLinkedTicketsFilters({
  filter,
  choicesData,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: LookUpLinkedTicketsFiltersProps): ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
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
  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
      isOnPaper={false}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filters-search"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            label={t('Status')}
            value={filter.status || null}
            data-cy="filters-status"
          >
            {choicesData.grievanceTicketStatusChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            label={t('FSP')}
            value={filter.fsp}
            onChange={(e) => handleFilterChange('fsp', e.target.value)}
            data-cy="filters-fsp"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            topLabel={t('Creation Date')}
            label="From"
            onChange={(date) => handleFilterChange('createdAtRangeMin', date)}
            value={filter.createdAtRangeMin}
            dataCy="filters-creation-date-from"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            label={t('To')}
            onChange={(date) => handleFilterChange('createdAtRangeMax', date)}
            value={filter.createdAtRangeMax}
            dataCy="filters-creation-date-to"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <AdminAreaAutocomplete
            level={2}
            name="admin2"
            value={filter.admin2}
            setFilter={setFilter}
            filter={filter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy="filters-admin"
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
