import { Grid } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { TargetPopulationAutocompleteRestFilter } from '@shared/autocompletes/rest/TargetPopulationAutocompleteRestFilter';
import { createHandleApplyFilterChange } from '@utils/utils';
import { DatePickerFilter } from '@core/DatePickerFilter';
import { FiltersSection } from '@core/FiltersSection';
import { SearchTextField } from '@core/SearchTextField';
import type { ReactElement } from 'react';
import { CreatedByAutocompleteRestFilter } from '@shared/autocompletes/CreatedByAutocompleteRestFilter';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

interface SurveysFiltersProps {
  filter: Record<string, any>;
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
      <ResponsiveGridContainer spacing={3} sx={{ alignItems: 'center' }}>
        <ResponsiveGrid size="third">
          <SearchTextField
            value={filter.search}
            label="Search"
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filters-search"
            fullWidth
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="third">
          <TargetPopulationAutocompleteRestFilter
            name="targetPopulation"
            value={filter.targetPopulation}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="third">
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
        </ResponsiveGrid>
        <Grid
          container
          size={{ xs: 12 }}
          spacing={3}
          sx={{ alignItems: 'flex-end' }}
        >
          <ResponsiveGrid size="quarter" mobileSize="half">
            <DatePickerFilter
              topLabel={t('Creation Date')}
              label="From"
              onChange={(date) => handleFilterChange('createdAtRangeMin', date)}
              value={filter.createdAtRangeMin}
              dataCy="filters-creation-date-from"
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <DatePickerFilter
              label={t('To')}
              onChange={(date) => handleFilterChange('createdAtRangeMax', date)}
              value={filter.createdAtRangeMax}
              dataCy="filters-creation-date-to"
            />
          </ResponsiveGrid>
        </Grid>
      </ResponsiveGridContainer>
    </FiltersSection>
  );
}
