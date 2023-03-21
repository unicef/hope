import { Grid, MenuItem } from '@material-ui/core';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { AssigneeAutocomplete } from '../../../../shared/autocompletes/AssigneeAutocomplete';
import { createHandleFilterChange } from '../../../../utils/utils';
import {
  useAllProgramsForChoicesQuery,
  useAllTargetPopulationForChoicesQuery
} from '../../../../__generated__/graphql';
import { ContainerWithBorder } from '../../../core/ContainerWithBorder';
import { DatePickerFilter } from '../../../core/DatePickerFilter';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { SelectFilter } from '../../../core/SelectFilter';

interface CommunicationFiltersProps {
  onFilterChange;
  filter;
}
export const CommunicationFilters = ({
  onFilterChange,
  filter,
}: CommunicationFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );
  const businessArea = useBusinessArea();
  const { data, loading: programsLoading } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });

  const {
    data: allTargetPopulationForChoices,
    loading: targetPopulationsLoading,
  } = useAllTargetPopulationForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });

  const allPrograms = data?.allPrograms?.edges || [];
  const programs = allPrograms.map((edge) => edge.node);

  const allTargetPopulations =
    allTargetPopulationForChoices?.allTargetPopulation?.edges || [];
  const targetPopulations = allTargetPopulations.map((edge) => edge.node);

  if (programsLoading || targetPopulationsLoading) return <LoadingComponent />;

  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('program', e.target.value)}
            label={t('Programme')}
            value={filter.program}
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
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('targetPopulation', e.target.value)
            }
            label={t('Target Population')}
            value={filter.targetPopulation}
            fullWidth
          >
            <MenuItem value=''>
              <em>{t('None')}</em>
            </MenuItem>
            {targetPopulations.map((program) => (
              <MenuItem key={program.id} value={program.id}>
                {program.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <AssigneeAutocomplete
            onFilterChange={onFilterChange}
            name='createdBy'
            value={filter.createdBy}
            filter={filter}
            label={t('Created by')}
            fullWidth
          />
        </Grid>
        <Grid container item xs={3} spacing={3} alignItems='flex-end'>
          <Grid item xs={6}>
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
          <Grid item xs={6}>
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
    </ContainerWithBorder>
  );
};
