import { Grid, MenuItem } from '@material-ui/core';
import ViewModuleRoundedIcon from '@material-ui/icons/ViewModuleRounded';
import React from 'react';
import { useTranslation } from 'react-i18next';
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
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });

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
            value={filter.search || ''}
            onChange={(e) => handleFilterChange(e, 'search')}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'module')}
            label={t('Module')}
            value={filter.module || ''}
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
            {Object.entries(modules).map(([key, value]) => (
              <MenuItem key={key} value={key}>
                {value}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
