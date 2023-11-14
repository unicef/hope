import { Grid, MenuItem } from '@material-ui/core';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { useAllProgramsForChoicesQuery } from '../../__generated__/graphql';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { AdminAreaAutocomplete } from '../../shared/autocompletes/AdminAreaAutocomplete';
import { createHandleApplyFilterChange } from '../../utils/utils';
import { FiltersSection } from '../core/FiltersSection';
import { LoadingComponent } from '../core/LoadingComponent';
import { SelectFilter } from '../core/SelectFilter';

interface DashboardFiltersProps {
  filter;
  setFilter;
  initialFilter;
  appliedFilter;
  setAppliedFilter;
}

interface ProgramSelectProps {
  onChange: CallableFunction;
  value: string;
}

const ProgramSelect = ({
  onChange,
  value,
}: ProgramSelectProps): React.ReactElement => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const { data, loading } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });
  if (loading) return <LoadingComponent />;

  const allPrograms = data?.allPrograms?.edges || [];
  const programs = allPrograms.map((edge) => edge.node);

  return (
    <SelectFilter
      onChange={onChange}
      label={t('Programme')}
      value={value}
      icon={<FlashOnIcon />}
      data-cy='filter-program'
      fullWidth
    >
      {programs.map((program) => (
        <MenuItem key={program.id} value={program.id}>
          {program.name}
        </MenuItem>
      ))}
    </SelectFilter>
  );
};

export const DashboardFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: DashboardFiltersProps): React.ReactElement => {
  const history = useHistory();
  const location = useLocation();
  const { isAllPrograms } = useBaseUrl();

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

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <Grid container alignItems='flex-end' spacing={3}>
        {isAllPrograms && (
          <Grid item xs={5}>
            <ProgramSelect
              onChange={(e) => handleFilterChange('program', e.target.value)}
              value={filter.program}
            />
          </Grid>
        )}
        <Grid item xs={3}>
          <AdminAreaAutocomplete
            fullWidth
            name='administrativeArea'
            value={filter.administrativeArea}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy='filter-administrative-area'
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
};
