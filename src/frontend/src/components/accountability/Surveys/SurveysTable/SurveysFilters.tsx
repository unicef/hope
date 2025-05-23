import { Grid2 as Grid } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { TargetPopulationAutocomplete } from '@shared/autocompletes/TargetPopulationAutocomplete';
import { createHandleApplyFilterChange } from '@utils/utils';
import { DatePickerFilter } from '@core/DatePickerFilter';
import { FiltersSection } from '@core/FiltersSection';
import { SearchTextField } from '@core/SearchTextField';
import { ReactElement } from 'react';
import { CreatedByAutocompleteRestFilter } from '@shared/autocompletes/CreatedByAutocompleteRestFilter';

interface SurveysFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export function SurveysFilters({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: SurveysFiltersProps): ReactElement {
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useTranslation();
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
      applyHandler={handleApplyFilter}
      clearHandler={handleClearFilter}
    >
      <Grid container alignItems="center" spacing={3}>
        <Grid size={{ xs: 4 }}>
          <SearchTextField
            value={filter.search}
            label="Search"
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filters-search"
            fullWidth
          />
        </Grid>
        <Grid size={{ xs: 4 }}>
          <TargetPopulationAutocomplete
            name="targetPopulation"
            value={filter.targetPopulation}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </Grid>
        <Grid size={{ xs: 4 }}>
          <CreatedByAutocompleteRestFilter
            name="createdBy"
            label={t('Created by')}
            value={filter.createdBy}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            additionalVariables={{ isSurveyCreator: true }}
          />
        </Grid>
        <Grid container size={{ xs: 12 }} spacing={3} alignItems="flex-end">
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
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
