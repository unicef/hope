import { Grid, MenuItem } from '@material-ui/core';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import React from 'react';
import { useTranslation } from 'react-i18next';
import moment from 'moment';
import { SelectFilter } from '../../../core/SelectFilter';
import { ContainerWithBorder } from '../../../core/ContainerWithBorder';
import {
  useAllProgramsForChoicesQuery,
  useAllTargetPopulationForChoicesQuery,
} from '../../../../__generated__/graphql';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { DatePickerFilter } from '../../../core/DatePickerFilter';

interface CommunicationFiltersProps {
  onFilterChange;
  filter;
}
export function CommunicationFilters({
  onFilterChange,
  filter,
}: CommunicationFiltersProps): React.ReactElement {
  const { t } = useTranslation();
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
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });

  if (programsLoading || targetPopulationsLoading) return <LoadingComponent />;

  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'program')}
            label={t('Programme')}
            value={filter.program || ''}
            icon={<FlashOnIcon />}
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
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'targetPopulation')}
            label={t('Target Population')}
            value={filter.targetPopulation || ''}
          >
            {targetPopulations.map((program) => (
              <MenuItem key={program.id} value={program.id}>
                {program.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item>
          <DatePickerFilter
            topLabel={t('Creation Date')}
            label='From'
            onChange={(date) =>
              onFilterChange({
                ...filter,
                createdAtRange: {
                  ...filter.createdAtRange,
                  min: moment(date)
                    .startOf('day')
                    .toISOString(),
                },
              })
            }
            value={filter.createdAtRange.min}
          />
        </Grid>
        <Grid item>
          <DatePickerFilter
            label={t('To')}
            onChange={(date) =>
              onFilterChange({
                ...filter,
                createdAtRange: {
                  ...filter.createdAtRange,
                  max: moment(date)
                    .endOf('day')
                    .toISOString(),
                },
              })
            }
            value={filter.createdAtRange.max}
          />
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
