import { Grid, MenuItem } from '@material-ui/core';
import { useHistory, useLocation } from 'react-router-dom';
import ViewModuleRoundedIcon from '@material-ui/icons/ViewModuleRounded';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { createHandleFilterChange } from '../../utils/utils';
import {AssigneeAutocomplete} from "../../shared/AssigneeAutocomplete";
import { ContainerWithBorder } from './ContainerWithBorder';
import { SearchTextField } from './SearchTextField';
import { SelectFilter } from './SelectFilter';

interface ActivityLogPageFiltersProps {
  onFilterChange;
  filter;
}
export function ActivityLogPageFilters({
  onFilterChange,
  filter,
}: ActivityLogPageFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );

  const modules = {
    program: 'Programme',
    household: 'Household',
    individual: 'Individual',
    grievanceticket: 'Grievance ticket',
    paymentverificationplan: 'Cash plan payment verification',
    targetpopulation: 'Target Population',
    registrationdataimport: 'Registration data import',
  };
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange('module', e.target.value)}
            label={t('Module')}
            value={filter.module}
            icon={<ViewModuleRoundedIcon />}
            SelectDisplayProps={{
              'data-cy': 'filters-residence-status',
            }}
            MenuProps={{
              'data-cy': 'filters-residence-status-options',
            }}
          >
            <MenuItem value=''>
              <em>{t('None')}</em>
            </MenuItem>
            {Object.entries(modules)
              .sort()
              .map(([key, value]) => (
                <MenuItem key={key} value={key}>
                  {value}
                </MenuItem>
              ))}
          </SelectFilter>
        </Grid>
        <Grid item>
          <AssigneeAutocomplete
            label="User"
            onFilterChange={onFilterChange}
            filter={filter}
            name='userId'
            value={filter.userId}
          />
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
