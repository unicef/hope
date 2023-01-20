import { Grid, MenuItem } from '@material-ui/core';
import { Group, Person } from '@material-ui/icons';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { targetPopulationStatusMapping } from '../../../utils/utils';
import {
  ProgramNode,
  TargetPopulationStatus,
} from '../../../__generated__/graphql';
import { ContainerWithBorder } from '../../core/ContainerWithBorder';
import { NumberTextField } from '../../core/NumberTextField';
import { SearchTextField } from '../../core/SearchTextField';
import { SelectFilter } from '../../core/SelectFilter';

interface EnrollmentsFiltersProps {
  onFilterChange;
  filter;
}
export function EnrollmentsFilters({
  onFilterChange,
  filter,
}: EnrollmentsFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
            value={filter.name}
            onChange={(e) => handleFilterChange(e, 'name')}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'status')}
            value={filter.status}
            label={t('Status')}
          >
            <MenuItem value=''>None</MenuItem>
            {Object.values(TargetPopulationStatus)
              .sort()
              .map((key) => (
                <MenuItem key={key} value={key}>
                  {targetPopulationStatusMapping(key)}
                </MenuItem>
              ))}
          </SelectFilter>
        </Grid>
        <Grid item>
          <NumberTextField
            topLabel={t('Household Size')}
            value={filter.size.min}
            placeholder={t('From')}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                size: {
                  ...filter.size,
                  min: e.target.value,
                },
              })
            }
            icon={<Group />}
          />
        </Grid>
        <Grid item>
          <NumberTextField
            value={filter.size.max}
            placeholder={t('To')}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                size: {
                  ...filter.size,
                  max: e.target.value,
                },
              })
            }
            icon={<Group />}
          />
        </Grid>
        <Grid item>
          <NumberTextField
            topLabel={t('Number of Individuals')}
            value={filter.numIndividuals.min}
            placeholder={t('From')}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                numIndividuals: {
                  ...filter.numIndividuals,
                  min: e.target.value,
                },
              })
            }
            icon={<Group />}
          />
        </Grid>
        <Grid item>
          <NumberTextField
            value={filter.numIndividuals.max}
            placeholder={t('To')}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                numIndividuals: {
                  ...filter.numIndividuals,
                  max: e.target.value,
                },
              })
            }
            icon={<Group />}
          />
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
