import { Grid, MenuItem } from '@material-ui/core';
import { Group, Person } from '@material-ui/icons';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import {
  createHandleFilterChange,
  targetPopulationStatusMapping,
} from '../../utils/utils';
import {
  ProgramNode,
  TargetPopulationStatus,
} from '../../__generated__/graphql';
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
export const TargetPopulationFilters = ({
  onFilterChange,
  filter,
  programs,
  addBorder = true,
}: TargetPopulationFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );

  const renderTable = (): React.ReactElement => (
    <Grid container alignItems='flex-end' spacing={3}>
      <Grid item xs={4}>
        <SearchTextField
          label={t('Search')}
          value={filter.name}
          onChange={(e) => handleFilterChange('name', e.target.value)}
          data-cy='filters-search'
          fullWidth
        />
      </Grid>
      <Grid item xs={4}>
        <SelectFilter
          onChange={(e) => handleFilterChange('status', e.target.value)}
          value={filter.status}
          label={t('Status')}
          icon={<Person />}
          fullWidth
          data-cy='filters-status'
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
      <Grid item xs={4}>
        <SelectFilter
          onChange={(e) => handleFilterChange('program', e.target.value)}
          label={t('Programme')}
          value={filter.program}
          icon={<FlashOnIcon />}
          fullWidth
          data-cy='filters-program'
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
      <Grid container item xs={4} spacing={3} alignItems='flex-end'>
        <Grid item xs={6}>
          <NumberTextField
            topLabel={t('Number of Households')}
            value={filter.numIndividualsMin}
            placeholder={t('From')}
            onChange={(e) =>
              handleFilterChange('numIndividualsMin', e.target.value)
            }
            icon={<Group />}
            data-cy='filters-num-individuals-min'
          />
        </Grid>
        <Grid item xs={6}>
          <NumberTextField
            value={filter.numIndividualsMax}
            placeholder={t('To')}
            onChange={(e) =>
              handleFilterChange('numIndividualsMax', e.target.value)
            }
            icon={<Group />}
            data-cy='filters-num-individuals-max'
          />
        </Grid>
      </Grid>
      <Grid container item xs={4} spacing={3} alignItems='flex-end'>
        <Grid item xs={6}>
          <DatePickerFilter
            topLabel={t('Date Created')}
            placeholder={t('From')}
            onChange={(date) =>
              handleFilterChange(
                'createdAtRangeMin',
                moment(date).format('YYYY-MM-DD'),
              )
            }
            value={filter.createdAtRangeMin}
          />
        </Grid>
        <Grid item xs={6}>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) =>
              handleFilterChange(
                'createdAtRangeMax',
                moment(date).format('YYYY-MM-DD'),
              )
            }
            value={filter.createdAtRangeMax}
          />
        </Grid>
      </Grid>
    </Grid>
  );

  return addBorder ? (
    <ContainerWithBorder>{renderTable()}</ContainerWithBorder>
  ) : (
    renderTable()
  );
};
