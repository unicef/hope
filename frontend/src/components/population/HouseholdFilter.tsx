import { Grid, MenuItem } from '@material-ui/core';
import AssignmentIndRoundedIcon from '@material-ui/icons/AssignmentIndRounded';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import GroupIcon from '@material-ui/icons/Group';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { createHandleFilterChange } from '../../utils/utils';
import {
  HouseholdChoiceDataQuery,
  ProgramNode,
} from '../../__generated__/graphql';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { NumberTextField } from '../core/NumberTextField';
import { SearchTextField } from '../core/SearchTextField';
import { SelectFilter } from '../core/SelectFilter';
import { AdminAreaAutocomplete } from './AdminAreaAutocomplete';

interface HouseholdFiltersProps {
  onFilterChange;
  filter;
  programs: ProgramNode[];
  choicesData: HouseholdChoiceDataQuery;
}

const orderOptions = [
  { name: 'Household Id: ascending', value: 'unicef_id' },
  { name: 'Household Id: descending', value: '-unicef_id' },
  { name: 'Status: ascending', value: 'status_label' },
  { name: 'Status: descending', value: '-status_label' },
  { name: 'Household Size: ascending', value: 'size' },
  { name: 'Household Size: descending', value: '-size' },
];
export const HouseholdFilters = ({
  onFilterChange,
  filter,
  programs,
  choicesData,
}: HouseholdFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );

  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
            value={filter.text}
            onChange={(e) => handleFilterChange('text', e.target.value)}
            data-cy='hh-filters-search'
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange('program', e.target.value)}
            label={t('Programme')}
            value={filter.program}
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
            onChange={(e) =>
              handleFilterChange('residenceStatus', e.target.value)
            }
            label={t('Residence Status')}
            value={filter.residenceStatus}
            icon={<AssignmentIndRoundedIcon />}
            SelectDisplayProps={{
              'data-cy': 'filters-residence-status',
            }}
            MenuProps={{
              'data-cy': 'filters-residence-status-options',
            }}
          >
            {choicesData.residenceStatusChoices?.map((status) => (
              <MenuItem key={status.value} value={status.value}>
                {status.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item>
          <AdminAreaAutocomplete
            name='admin2'
            value={filter.admin2}
            onFilterChange={onFilterChange}
            filter={filter}
          />
        </Grid>
        <Grid item>
          <NumberTextField
            topLabel={t('Household Size')}
            value={filter.householdSizeMin}
            placeholder={t('From')}
            icon={<GroupIcon />}
            onChange={(e) =>
              handleFilterChange('householdSizeMin', e.target.value)
            }
          />
        </Grid>
        <Grid item>
          <NumberTextField
            value={filter.householdSizeMax}
            placeholder={t('To')}
            icon={<GroupIcon />}
            onChange={(e) =>
              handleFilterChange('householdSizeMax', e.target.value)
            }
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange('orderBy', e.target.value)}
            label={t('Sort by')}
            value={filter.orderBy}
          >
            <MenuItem value=''>
              <em>{t('None')}</em>
            </MenuItem>
            {orderOptions.map((order) => (
              <MenuItem key={order.value} value={order.value}>
                {order.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
};
