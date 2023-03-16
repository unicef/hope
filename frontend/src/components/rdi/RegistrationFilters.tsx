<<<<<<< HEAD
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
import { AssigneeAutocomplete } from '../../shared/autocompletes/AssigneeAutocomplete';
=======
import { InputAdornment, MenuItem } from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import moment from 'moment';
import React from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import TextField from '../../shared/TextField';
import { useRegistrationChoicesQuery } from '../../__generated__/graphql';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { DatePickerFilter } from '../core/DatePickerFilter';
import { SelectFilter } from '../core/SelectFilter';
import { AssigneeAutocomplete } from '../../shared/AssigneeAutocomplete/AssigneeAutocomplete';
import { createHandleFilterChange } from '../../utils/utils';

const StyledTextField = styled(TextField)`
  flex: 1;
  && {
    min-width: 150px;
  }
`;
>>>>>>> origin

interface RegistrationFiltersProps {
  onFilterChange;
  filter;
<<<<<<< HEAD
  addBorder?: boolean;
}
export function RegistrationFilters({
  onFilterChange,
  filter,
  addBorder = true,
}: RegistrationFiltersProps): React.ReactElement {
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
=======
}
export const RegistrationFilters = ({
  onFilterChange,
  filter,
}: RegistrationFiltersProps): React.ReactElement => {
  const history = useHistory();
  const location = useLocation();

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );

>>>>>>> origin
  const { t } = useTranslation();
  const { data: registrationChoicesData } = useRegistrationChoicesQuery();
  if (!registrationChoicesData) {
    return null;
  }

<<<<<<< HEAD
  const renderTable = (): React.ReactElement => {
    return (
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) =>
              onFilterChange({ ...filter, search: e.target.value })
            }
            data-cy='filters-search'
            fullWidth
          />
        </Grid>
        <Grid item xs={3}>
          <AssigneeAutocomplete
            onFilterChange={onFilterChange}
            name='importedBy'
            label={t('Imported By')}
            fullWidth
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            value={filter.status}
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
              value={filter.size.min}
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
              value={filter.size.max}
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
=======
  return (
    <ContainerWithBorder>
      <StyledTextField
        variant='outlined'
        label={t('Search')}
        margin='dense'
        onChange={(e) => handleFilterChange('search', e.target.value)}
        value={filter.search}
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />
      <DatePickerFilter
        label={t('Import Date')}
        onChange={(date) =>
          handleFilterChange('importDate', moment(date).format('YYYY-MM-DD'))
        }
        value={filter.importDate}
      />
      <AssigneeAutocomplete
        name='importedBy'
        value={filter.importedBy}
        onFilterChange={onFilterChange}
        filter={filter}
        label={t('Imported By')}
      />
      <SelectFilter
        value={filter.status}
        label={t('Status')}
        onChange={(e) => handleFilterChange('status', e.target.value)}
      >
        <MenuItem value=''>
          <em>{t('None')}</em>
        </MenuItem>
        {registrationChoicesData.registrationDataStatusChoices.map((item) => {
          return (
            <MenuItem key={item.value} value={item.value}>
              {item.name}
            </MenuItem>
          );
        })}
      </SelectFilter>
    </ContainerWithBorder>
  );
};
>>>>>>> origin
