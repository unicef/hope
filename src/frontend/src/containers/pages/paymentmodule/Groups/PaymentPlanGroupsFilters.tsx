import { FiltersSection } from '@components/core/FiltersSection';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { createHandleApplyFilterChange } from '@utils/utils';
import { Grid, MenuItem } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';

interface PaymentPlanGroupsFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

export const PaymentPlanGroupsFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: PaymentPlanGroupsFiltersProps): ReactElement => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { businessArea, programId } = useBaseUrl();

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

  const { data: cycles } = useQuery({
    queryKey: ['programCyclesList', businessArea, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsCyclesList({
        businessAreaSlug: businessArea,
        programCode: programId,
        limit: 100,
        ordering: 'title',
      }),
    enabled: !!businessArea && !!programId,
  });

  return (
    <FiltersSection
      clearHandler={clearFilter}
      applyHandler={applyFilterChanges}
    >
      <Grid container spacing={3} alignItems="flex-end">
        <Grid size={4}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            fullWidth
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filters-search"
          />
        </Grid>
        <Grid size={4}>
          <SelectFilter
            onChange={(e) => handleFilterChange('cycle', e.target.value)}
            variant="outlined"
            label={t('Cycle')}
            value={filter.cycle}
            fullWidth
            data-cy="filters-cycle"
          >
            {(cycles?.results ?? []).map((cycle) => (
              <MenuItem key={cycle.id} value={cycle.id}>
                {cycle.title}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
      </Grid>
    </FiltersSection>
  );
};
