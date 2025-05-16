import { Grid2 as Grid } from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { AdminAreaAutocomplete } from '@shared/autocompletes/AdminAreaAutocomplete';
import { createHandleApplyFilterChange } from '@utils/utils';
import { FiltersSection } from '@core/FiltersSection';
import { ReactElement } from 'react';
import { ProgramAutocompleteRestFilter } from '@shared/autocompletes/ProgramAutocompleteRestFilter';

interface DashboardFiltersProps {
  filter;
  setFilter;
  initialFilter;
  appliedFilter;
  setAppliedFilter;
}

export const DashboardFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: DashboardFiltersProps): ReactElement => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAllPrograms } = useBaseUrl();

  const { applyFilterChanges, clearFilter } = createHandleApplyFilterChange(
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
    >
      <Grid container alignItems="flex-end" spacing={3}>
        {isAllPrograms && (
          <Grid size={{ xs: 5 }}>
            <ProgramAutocompleteRestFilter
              filter={filter}
              name="program"
              value={filter.program}
              setFilter={setFilter}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
            />
          </Grid>
        )}
        <Grid size={{ xs: 3 }}>
          <AdminAreaAutocomplete
            name="administrativeArea"
            level={2}
            value={filter.administrativeArea}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy="filter-administrative-area"
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
};
