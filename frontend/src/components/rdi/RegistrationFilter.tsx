import { Grid, MenuItem } from '@material-ui/core';
import React from 'react';
import GroupIcon from '@material-ui/icons/Group';
import { useTranslation } from 'react-i18next';
import moment from 'moment';
import { useRegistrationChoicesQuery } from '../../__generated__/graphql';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { DatePickerFilter } from '../core/DatePickerFilter';
import { NumberTextField } from '../core/NumberTextField';
import { SearchTextField } from '../core/SearchTextField';
import { SelectFilter } from '../core/SelectFilter';
import { UsersAutocomplete } from '../core/UsersAutocomplete';

interface RegistrationFiltersProps {
  onFilterChange;
  filter;
  addBorder?: boolean;
}
export function RegistrationFilters({
  onFilterChange,
  filter,
  addBorder = true,
}: RegistrationFiltersProps): React.ReactElement {
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  const { t } = useTranslation();
  const { data: registrationChoicesData } = useRegistrationChoicesQuery();
  if (!registrationChoicesData) {
    return null;
  }

  const renderTable = (): React.ReactElement => {
    return (
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.search || ''}
            onChange={(e) =>
              onFilterChange({ ...filter, search: e.target.value })
            }
            data-cy='filters-search'
            fullWidth
          />
        </Grid>
        <Grid item xs={3}>
          <UsersAutocomplete
            onInputTextChange={(value) =>
              onFilterChange({ ...filter, userInputValue: value })
            }
            fullWidth
            inputValue={filter.userInputValue}
            onChange={(e, option) => {
              if (!option) {
                onFilterChange({ ...filter, importedBy: undefined });
                return;
              }
              onFilterChange({ ...filter, importedBy: option.node.id });
            }}
            value={filter.importedBy}
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            value={filter.status || ''}
            label={t('Status')}
            onChange={(e) => handleFilterChange(e, 'status')}
            fullWidth
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
        <Grid container item xs={3} spacing={3} alignItems='flex-end'>
          <Grid item xs={6}>
            <NumberTextField
              id='minFilter'
              topLabel={t('Household Size')}
              value={filter.size.min || ''}
              placeholder='From'
              icon={<GroupIcon />}
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  size: {
                    ...filter.size,
                    min: e.target.value || undefined,
                  },
                })
              }
            />
          </Grid>
          <Grid item xs={6}>
            <NumberTextField
              id='maxFilter'
              value={filter.size.max || ''}
              placeholder='To'
              icon={<GroupIcon />}
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  size: {
                    ...filter.size,
                    max: e.target.value || undefined,
                  },
                })
              }
            />
          </Grid>
        </Grid>
        <Grid container item xs={3} spacing={3} alignItems='flex-end'>
          <Grid item xs={6}>
            <DatePickerFilter
              topLabel={t('Import Date')}
              placeholder={t('From')}
              onChange={(date) =>
                onFilterChange({
                  ...filter,
                  importDateRange: {
                    ...filter.importDateRange,
                    min: date ? moment(date).format('YYYY-MM-DD') : null,
                  },
                })
              }
              value={filter.importDateRange.min}
            />
          </Grid>
          <Grid item xs={6}>
            <DatePickerFilter
              placeholder={t('To')}
              onChange={(date) =>
                onFilterChange({
                  ...filter,
                  importDateRange: {
                    ...filter.importDateRange,
                    max: date ? moment(date).format('YYYY-MM-DD') : null,
                  },
                })
              }
              value={filter.importDateRange.max}
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
