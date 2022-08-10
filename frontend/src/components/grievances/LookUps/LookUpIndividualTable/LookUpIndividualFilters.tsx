import {
  Button,
  Checkbox,
  FormControlLabel,
  Grid,
  MenuItem,
} from '@material-ui/core';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import WcIcon from '@material-ui/icons/Wc';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ContainerWithBorder } from '../../../core/ContainerWithBorder';
import { DatePickerFilter } from '../../../core/DatePickerFilter';
import { SearchTextField } from '../../../core/SearchTextField';
import { SelectFilter } from '../../../core/SelectFilter';
import { AdminAreaAutocomplete } from '../../../population/AdminAreaAutocomplete';

interface LookUpIndividualFiltersProps {
  onFilterChange;
  filter;
  programs;
  setFilterIndividualApplied?;
  individualFilterInitial?;
  household?;
  addBorder?;
}
export function LookUpIndividualFilters({
  onFilterChange,
  filter,
  programs,
  setFilterIndividualApplied,
  individualFilterInitial,
  household,
  addBorder = true,
}: LookUpIndividualFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });

  const renderTable = (): React.ReactElement => {
    return (
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange(e, 'search')}
            data-cy='filters-search'
            fullWidth
          />
        </Grid>
        <Grid item container xs={5}>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'programs')}
            label={t('Programme')}
            value={filter.programs || []}
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
        <Grid item xs={2}>
          <DatePickerFilter
            topLabel={t('Registration Date')}
            placeholder={t('From')}
            onChange={(date) =>
              onFilterChange({
                ...filter,
                lastRegistrationDate: {
                  ...filter.lastRegistrationDate,
                  min: date ? moment(date).format('YYYY-MM-DD') : null,
                },
              })
            }
            value={filter.lastRegistrationDate.min}
          />
        </Grid>
        <Grid item xs={2}>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) =>
              onFilterChange({
                ...filter,
                lastRegistrationDate: {
                  ...filter.lastRegistrationDate,
                  max: date ? moment(date).format('YYYY-MM-DD') : null,
                },
              })
            }
            value={filter.lastRegistrationDate.max}
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'status')}
            multiple
            label={t('Status')}
            value={filter.status || []}
            fullWidth
          >
            {[
              { value: 'ACTIVE', name: 'Active' },
              { value: 'WITHDRAWN', name: 'Withdrawn' },
              { value: 'DUPLICATE', name: 'Duplicate' },
            ].map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item xs={5}>
          <AdminAreaAutocomplete
            onFilterChange={onFilterChange}
            name='admin2'
            value={filter.admin2}
            fullWidth
          />
        </Grid>
        <Grid item xs={4}>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'sex')}
            value={filter.sex || ''}
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
            <MenuItem value='MALE'>{t('Male')}</MenuItem>
            <MenuItem value='FEMALE'>{t('Female')}</MenuItem>
          </SelectFilter>
        </Grid>
        {household && (
          <Grid item>
            <FormControlLabel
              control={
                <Checkbox
                  checked={filter.household}
                  color='primary'
                  onChange={(e) => {
                    if (e.target.checked) {
                      onFilterChange({ ...filter, household: household.id });
                    } else {
                      onFilterChange({ ...filter, household: null });
                    }
                  }}
                />
              }
              label={t('Show only Individuals from this household')}
            />
          </Grid>
        )}
        <Grid container justify='flex-end'>
          <Button
            color='primary'
            onClick={() => {
              setFilterIndividualApplied(individualFilterInitial);
              onFilterChange(individualFilterInitial);
            }}
          >
            {t('Clear')}
          </Button>
          <Button
            color='primary'
            variant='outlined'
            onClick={() => setFilterIndividualApplied(filter)}
          >
            {t('Apply')}
          </Button>
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
