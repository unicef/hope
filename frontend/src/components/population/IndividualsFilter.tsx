import { Grid, MenuItem } from '@material-ui/core';
import CakeIcon from '@material-ui/icons/Cake';
import WcIcon from '@material-ui/icons/Wc';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { IndividualChoiceDataQuery } from '../../__generated__/graphql';
import { createHandleApplyFilterChange } from '../../utils/utils';
import { ClearApplyButtons } from '../core/ClearApplyButtons';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { NumberTextField } from '../core/NumberTextField';
import { SearchTextField } from '../core/SearchTextField';
import { SelectFilter } from '../core/SelectFilter';
import { AdminAreaAutocomplete } from '../../shared/autocompletes/AdminAreaAutocomplete';

interface IndividualsFilterProps {
  filter;
  choicesData: IndividualChoiceDataQuery;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

const orderOptions = [
  { name: 'Individual Id: ascending', value: 'unicef_id' },
  { name: 'Individual Id: descending', value: '-unicef_id' },
  { name: 'Individual: ascending', value: 'full_name' },
  { name: 'Individual: descending', value: '-full_name' },
  { name: 'Gender: ascending', value: 'sex' },
  { name: 'Gender: descending', value: '-sex' },
];

export const IndividualsFilter = ({
  filter,
  choicesData,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: IndividualsFilterProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();

  const {
    handleFilterChange,
    applyFilterChanges,
    clearFilter,
  } = createHandleApplyFilterChange(
    initialFilter,
    history,
    location,
    filter,
    setFilter,
    appliedFilter,
    setAppliedFilter,
  );

  const handleApplyFilter = (): void => {
    applyFilterChanges();
  };

  const handleClearFilter = (): void => {
    clearFilter();
  };

  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.text}
            onChange={(e) => handleFilterChange('text', e.target.value)}
            data-cy='ind-filters-search'
          />
        </Grid>
        <Grid item xs={3}>
          <AdminAreaAutocomplete
            name='admin2'
            value={filter.admin2}
            setFilter={setFilter}
            filter={filter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('sex', e.target.value)}
            value={filter.sex}
            label={t('Gender')}
            icon={<WcIcon />}
            SelectDisplayProps={{
              'data-cy': 'filters-sex',
            }}
            MenuProps={{
              'data-cy': 'filters-sex-options',
            }}
            fullWidth
          >
            <MenuItem value=''>
              <em>{t('None')}</em>
            </MenuItem>
            <MenuItem value='FEMALE'>{t('Female')}</MenuItem>
            <MenuItem value='MALE'>{t('Male')}</MenuItem>
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            fullWidth
            topLabel={t('Age')}
            placeholder={t('From')}
            value={filter.ageMin}
            onChange={(e) => {
              if (e.target.value < 0 || e.target.value > 120) return;
              handleFilterChange('ageMin', e.target.value);
            }}
            icon={<CakeIcon />}
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            fullWidth
            placeholder={t('To')}
            value={filter.ageMax}
            onChange={(e) => {
              if (e.target.value < 0 || e.target.value > 120) return;
              handleFilterChange('ageMax', e.target.value);
            }}
            icon={<CakeIcon />}
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('flags', e.target.value)}
            label={t('Flags')}
            multiple
            fullWidth
            value={filter.flags}
            SelectDisplayProps={{ 'data-cy': 'filters-flags' }}
            MenuProps={{
              'data-cy': 'filters-flags-options',
            }}
          >
            {choicesData?.flagChoices.map((each, index) => (
              <MenuItem
                key={each.value}
                value={each.value}
                data-cy={`select-option-${index}`}
              >
                {each.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('orderBy', e.target.value)}
            label={t('Sort by')}
            value={filter.orderBy}
            fullWidth
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
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            label={t('Status')}
            value={filter.status}
          >
            <MenuItem key='active' value='ACTIVE'>
              Active
            </MenuItem>
            <MenuItem key='duplicate' value='DUPLICATE'>
              Duplicate
            </MenuItem>
            <MenuItem key='withdrawn' value='WITHDRAWN'>
              Withdrawn
            </MenuItem>
          </SelectFilter>
        </Grid>
      </Grid>
      <ClearApplyButtons
        clearHandler={handleClearFilter}
        applyHandler={handleApplyFilter}
      />
    </ContainerWithBorder>
  );
};
