import { Grid, MenuItem } from '@material-ui/core';
import { Group, Person } from '@material-ui/icons';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { TARGETING_STATES } from '../../utils/constants';
import { ProgramNode } from '../../__generated__/graphql';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { DatePickerFilter } from '../core/DatePickerFilter';
import { NumberTextField } from '../core/NumberTextField';
import { SearchTextField } from '../core/SearchTextField';
import { SelectFilter } from '../core/SelectFilter';

interface TargetPopulationFiltersProps {
  onFilterChange;
  filter;
  programs: ProgramNode[];
  addBorder?: boolean;
}
export function TargetPopulationFilters({
  onFilterChange,
  filter,
  programs,
  addBorder = true,
}: TargetPopulationFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  const renderTable = (): React.ReactElement => {
    return (
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.name || ''}
            onChange={(e) => handleFilterChange(e, 'name')}
            data-cy='filters-search'
            fullWidth
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'status')}
            label={t('Status')}
            icon={<Person />}
            fullWidth
          >
            <MenuItem value=''>{TARGETING_STATES.NONE}</MenuItem>
            <MenuItem value='DRAFT'>{TARGETING_STATES.DRAFT}</MenuItem>
            <MenuItem value='LOCKED'>{TARGETING_STATES.LOCKED}</MenuItem>
            <MenuItem value='PROCESSING'>
              {TARGETING_STATES.PROCESSING}
            </MenuItem>
            <MenuItem value='READY_FOR_CASH_ASSIST'>
              {TARGETING_STATES.READY_FOR_CASH_ASSIST}
            </MenuItem>
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'program')}
            label={t('Programme')}
            value={filter.program || ''}
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
        <Grid container item xs={3} spacing={3} alignItems='flex-end'>
          <Grid item xs={6}>
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
          <Grid item xs={6}>
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
        <Grid container item xs={3} spacing={3} alignItems='flex-end'>
          <Grid item xs={6}>
            <DatePickerFilter
              topLabel={t('Date Created')}
              placeholder={t('From')}
              onChange={(date) =>
                onFilterChange({
                  ...filter,
                  createdAtRange: {
                    ...filter.createdAtRange,
                    min: date ? moment(date).format('YYYY-MM-DD') : null,
                  },
                })
              }
              value={filter.createdAtRange.min}
            />
          </Grid>
          <Grid item xs={6}>
            <DatePickerFilter
              placeholder={t('To')}
              onChange={(date) =>
                onFilterChange({
                  ...filter,
                  createdAtRange: {
                    ...filter.createdAtRange,
                    max: date ? moment(date).format('YYYY-MM-DD') : null,
                  },
                })
              }
              value={filter.createdAtRange.max}
            />
          </Grid>
        </Grid>
      </Grid>
    );
  };
  return addBorder ? (
    <ContainerWithBorder>{renderTable()}</ContainerWithBorder>
  ) : (
    renderTable()
  );
}
