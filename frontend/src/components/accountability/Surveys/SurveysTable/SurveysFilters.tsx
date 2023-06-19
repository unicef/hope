import { Grid, MenuItem } from '@material-ui/core';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import get from 'lodash/get';
import moment from 'moment';
import React from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { AssigneeAutocomplete } from '../../../../shared/autocompletes/AssigneeAutocomplete';
import { TargetPopulationAutocomplete } from '../../../../shared/autocompletes/TargetPopulationAutocomplete';
import { createHandleApplyFilterChange } from '../../../../utils/utils';
import { useAllProgramsForChoicesQuery } from '../../../../__generated__/graphql';
import { ContainerWithBorder } from '../../../core/ContainerWithBorder';
import { DatePickerFilter } from '../../../core/DatePickerFilter';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { SearchTextField } from '../../../core/SearchTextField';
import { SelectFilter } from '../../../core/SelectFilter';
import { ClearApplyButtons } from '../../../core/ClearApplyButtons';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';

interface SurveysFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const SurveysFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: SurveysFiltersProps): React.ReactElement => {
  const history = useHistory();
  const location = useLocation();
  const { businessArea } = useBaseUrl();
  const { t } = useTranslation();
  const { data, loading: programsLoading } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });

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

  if (programsLoading) return <LoadingComponent />;

  const allPrograms = get(data, 'allPrograms.edges', []);
  const programs = allPrograms.map((edge) => edge.node);

  return (
    <ContainerWithBorder>
      <Grid container alignItems='center' spacing={3}>
        <Grid xs={3} item>
          <SearchTextField
            value={filter.search}
            label='Search'
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy='filters-search'
            fullWidth
          />
        </Grid>
        <Grid xs={5} item>
          <SelectFilter
            onChange={(e) => handleFilterChange('program', e.target.value)}
            label={t('Programme')}
            value={filter.program}
            icon={<FlashOnIcon />}
            fullWidth
          >
            <MenuItem value=''>
              <em>{t('None')}</em>
            </MenuItem>
            {programs.map((program) => (
              <MenuItem key={program.id} value={program.id}>
                {program.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid xs={4} item>
          <TargetPopulationAutocomplete
            name='targetPopulation'
            value={filter.targetPopulation}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </Grid>
        <Grid container item xs={12} spacing={3} alignItems='flex-end'>
          <Grid item xs={4}>
            <AssigneeAutocomplete
              name='createdBy'
              label={t('Created by')}
              value={filter.createdBy}
              filter={filter}
              setFilter={setFilter}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
            />
          </Grid>
          <Grid item xs={4}>
            <DatePickerFilter
              topLabel={t('Creation Date')}
              label='From'
              onChange={(date) =>
                handleFilterChange(
                  'createdAtRangeMin',
                  moment(date)
                    .startOf('day')
                    .toISOString(),
                )
              }
              value={filter.createdAtRangeMin}
            />
          </Grid>
          <Grid item xs={4}>
            <DatePickerFilter
              label={t('To')}
              onChange={(date) =>
                handleFilterChange(
                  'createdAtRangeMax',
                  moment(date)
                    .endOf('day')
                    .toISOString(),
                )
              }
              value={filter.createdAtRangeMax}
            />
          </Grid>
        </Grid>
      </Grid>
      <ClearApplyButtons
        clearHandler={handleClearFilter}
        applyHandler={handleApplyFilter}
      />
    </ContainerWithBorder>
  );
};
