import { Grid } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { CreatedByAutocomplete } from '@shared/autocompletes/CreatedByAutocomplete';
import { TargetPopulationAutocomplete } from '@shared/autocompletes/TargetPopulationAutocomplete';
import { DatePickerFilter } from '@components/core/DatePickerFilter';
import { FiltersSection } from '@components/core/FiltersSection';
import { createHandleApplyFilterChange } from '@utils/utils';

interface CommunicationFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export function CommunicationFilters({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: CommunicationFiltersProps): React.ReactElement {
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

  return (
    <FiltersSection
      applyHandler={handleApplyFilter}
      clearHandler={handleClearFilter}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid xs={4} item>
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
        <Grid item xs={2}>
          <CreatedByAutocomplete
            label={t('Created by')}
            filter={filter}
            name="createdBy"
            value={filter.createdBy}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            additionalVariables={{ isMessageCreator: true }}
          />
        </Grid>
        <Grid container item xs={6} spacing={3} alignItems="flex-end">
          <Grid item xs={6}>
            <DatePickerFilter
              topLabel={t('Creation Date')}
              label="From"
              onChange={(date) => handleFilterChange('createdAtRangeMin', date)}
              value={filter.createdAtRangeMin}
              data-cy="filters-creation-date-from"
            />
          </Grid>
          <Grid item xs={6}>
            <DatePickerFilter
              label={t('To')}
              onChange={(date) => handleFilterChange('createdAtRangeMax', date)}
              value={filter.createdAtRangeMax}
              data-cy="filters-creation-date-to"
            />
          </Grid>
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
