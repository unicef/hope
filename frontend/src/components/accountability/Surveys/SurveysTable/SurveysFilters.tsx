import { Grid, MenuItem } from '@material-ui/core';
import get from 'lodash/get';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { TargetPopulationAutocomplete } from '../../../../shared/autocompletes/TargetPopulationAutocomplete';
import { useAllProgramsForChoicesQuery } from '../../../../__generated__/graphql';
import { ContainerWithBorder } from '../../../core/ContainerWithBorder';
import { DatePickerFilter } from '../../../core/DatePickerFilter';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { SearchTextField } from '../../../core/SearchTextField';
import { SelectFilter } from '../../../core/SelectFilter';
import { AssigneeAutocomplete } from '../../../../shared/autocompletes/AssigneeAutocomplete';

interface SurveysFiltersProps {
  onFilterChange;
  filter;
}
export const SurveysFilters = ({
  onFilterChange,
  filter,
}: SurveysFiltersProps): React.ReactElement => {
  const businessArea = useBusinessArea();
  const { t } = useTranslation();
  const { data, loading: programsLoading } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });

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
            onChange={(e) => handleFilterChange(e, 'search')}
            data-cy='filters-search'
            fullWidth
          />
        </Grid>
        <Grid xs={3} item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'program')}
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
        <Grid xs={3} item>
          <TargetPopulationAutocomplete
            onFilterChange={onFilterChange}
            name='targetPopulation'
            fullWidth
          />
        </Grid>
        <Grid item xs={3}>
          <AssigneeAutocomplete
            onFilterChange={onFilterChange}
            name='createdBy'
            label={t('Created by')}
            fullWidth
          />
        </Grid>
        <Grid container xs={6} item spacing={3} alignItems='flex-end'>
          <Grid item xs={6}>
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
          <Grid item xs={6}>
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
      </Grid>
    </ContainerWithBorder>
  );
};
