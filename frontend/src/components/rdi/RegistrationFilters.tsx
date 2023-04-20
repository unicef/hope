import { Grid, MenuItem } from '@material-ui/core';
import GroupIcon from '@material-ui/icons/Group';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { useRegistrationChoicesQuery } from '../../__generated__/graphql';
import { AssigneeAutocomplete } from '../../shared/autocompletes/AssigneeAutocomplete';
import { createHandleFilterChange } from '../../utils/utils';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { DatePickerFilter } from '../core/DatePickerFilter';
import { NumberTextField } from '../core/NumberTextField';
import { SearchTextField } from '../core/SearchTextField';
import { SelectFilter } from '../core/SelectFilter';

interface RegistrationFiltersProps {
  onFilterChange;
  filter;
  addBorder?: boolean;
}

export const RegistrationFilters = ({
  onFilterChange,
  filter,
  addBorder = true,
}: RegistrationFiltersProps): React.ReactElement => {
  const history = useHistory();
  const location = useLocation();

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );

  const { t } = useTranslation();
  const { data: registrationChoicesData } = useRegistrationChoicesQuery();
  if (!registrationChoicesData) {
    return null;
  }

  const renderTable = (): React.ReactElement => {
    return (
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={4}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy='filter-search'
            fullWidth
          />
        </Grid>
        <Grid item xs={4}>
          <AssigneeAutocomplete
            onFilterChange={onFilterChange}
            name='importedBy'
            label={t('Imported By')}
            fullWidth
            filter={filter}
            value={filter.importedBy}
            data-cy='filter-imported-by'
          />
        </Grid>
        <Grid item xs={4}>
          <SelectFilter
            value={filter.status}
            label={t('Status')}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            fullWidth
            data-cy='filter-status'
          >
            <MenuItem value=''>
              <em>{t('None')}</em>
            </MenuItem>
            {registrationChoicesData.registrationDataStatusChoices.map(
              (item) => {
                return (
                  <MenuItem key={item.value} value={item.value}>
                    {item.name}
                  </MenuItem>
                );
              },
            )}
          </SelectFilter>
        </Grid>
        <Grid container item xs={4} spacing={3} alignItems='flex-end'>
          <Grid item xs={6}>
            <NumberTextField
              id='minFilter'
              topLabel={t('Household Size')}
              value={filter.sizeMin}
              placeholder='From'
              icon={<GroupIcon />}
              onChange={(e) => handleFilterChange('sizeMin', e.target.value)}
              data-cy='filter-size-min'
            />
          </Grid>
          <Grid item xs={6}>
            <NumberTextField
              id='maxFilter'
              value={filter.sizeMax}
              placeholder='To'
              icon={<GroupIcon />}
              onChange={(e) => handleFilterChange('sizeMax', e.target.value)}
              data-cy='filter-size-max'
            />
          </Grid>
        </Grid>
        <Grid container item xs={4} spacing={3} alignItems='flex-end'>
          <Grid item xs={6}>
            <DatePickerFilter
              topLabel={t('Import Date')}
              placeholder={t('From')}
              onChange={(date) =>
                handleFilterChange(
                  'importDateRangeMin',
                  moment(date).format('YYYY-MM-DD'),
                )
              }
              value={filter.importDateRangeMin}
              data-cy='filter-import-date-range-min'
            />
          </Grid>
          <Grid item xs={6}>
            <DatePickerFilter
              placeholder={t('To')}
              onChange={(date) =>
                handleFilterChange(
                  'importDateRangeMax',
                  moment(date).format('YYYY-MM-DD'),
                )
              }
              value={filter.importDateRangeMax}
              data-cy='filter-import-date-range-max'
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
};
