import { Grid, MenuItem } from '@material-ui/core';
import { Group, Person } from '@material-ui/icons';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { TARGETING_STATES } from '../../utils/constants';
import { ProgramNode } from '../../__generated__/graphql';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { NumberTextField } from '../core/NumberTextField';
import { SearchTextField } from '../core/SearchTextField';
import { SelectFilter } from '../core/SelectFilter';

interface TargetPopulationFiltersProps {
  //targetPopulations: TargetPopulationNode[],
  onFilterChange;
  filter;
  programs: ProgramNode[];
}
export function TargetPopulationFilters({
  // targetPopulations,
  onFilterChange,
  filter,
  programs,
}: TargetPopulationFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
            value={filter.name || ''}
            onChange={(e) => handleFilterChange(e, 'name')}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'status')}
            label={t('Status')}
            icon={<Person />}
          >
            <MenuItem value=''>{TARGETING_STATES.NONE}</MenuItem>
            <MenuItem value='DRAFT'>{TARGETING_STATES.OPEN}</MenuItem>
            <MenuItem value='LOCKED'>{TARGETING_STATES.LOCKED}</MenuItem>
            <MenuItem value='PROCESSING'>
              {TARGETING_STATES.PROCESSING}
            </MenuItem>
            <MenuItem value='READY_FOR_CASH_ASSIST'>
              {TARGETING_STATES.READY_FOR_CASH_ASSIST}
            </MenuItem>
          </SelectFilter>
        </Grid>
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
          <NumberTextField
            id='minFilter'
            topLabel={t('Number of Households')}
            value={filter.numIndividuals.min}
            placeholder={t('From')}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                numIndividuals: {
                  ...filter.numIndividuals,
                  min: e.target.value || undefined,
                },
              })
            }
            icon={<Group />}
          />
        </Grid>
        <Grid item>
          <NumberTextField
            id='maxFilter'
            value={filter.numIndividuals.max}
            placeholder={t('To')}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                numIndividuals: {
                  ...filter.numIndividuals,
                  max: e.target.value || undefined,
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
