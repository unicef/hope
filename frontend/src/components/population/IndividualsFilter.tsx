import { Grid, MenuItem } from '@material-ui/core';
import CakeIcon from '@material-ui/icons/Cake';
import WcIcon from '@material-ui/icons/Wc';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { IndividualChoiceDataQuery } from '../../__generated__/graphql';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { NumberTextField } from '../core/NumberTextField';
import { SearchTextField } from '../core/SearchTextField';
import { SelectFilter } from '../core/SelectFilter';
import { AdminAreaAutocomplete } from '../../shared/autocompletes/AdminAreaAutocomplete';

interface IndividualsFilterProps {
  onFilterChange;
  filter;
  choicesData: IndividualChoiceDataQuery;
}

export const IndividualsFilter = ({
  onFilterChange,
  filter,
  choicesData,
}: IndividualsFilterProps): React.ReactElement => {
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
            value={filter.text}
            onChange={(e) => handleFilterChange(e, 'text')}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item>
          <AdminAreaAutocomplete
            onFilterChange={onFilterChange}
            name='adminArea'
          />
        </Grid>
        <Grid item>
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
          >
            <MenuItem value=''>
              <em>{t('None')}</em>
            </MenuItem>
            <MenuItem value='MALE'>{t('Male')}</MenuItem>
            <MenuItem value='FEMALE'>{t('Female')}</MenuItem>
          </SelectFilter>
        </Grid>
        <Grid item>
          <NumberTextField
            topLabel={t('Age')}
            placeholder={t('From')}
            value={filter.age.min}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                age: { ...filter.age, min: e.target.value || undefined },
              })
            }
            icon={<CakeIcon />}
          />
        </Grid>
        <Grid item>
          <NumberTextField
            placeholder={t('To')}
            value={filter.age.max}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                age: { ...filter.age, max: e.target.value || undefined },
              })
            }
            icon={<CakeIcon />}
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'flags')}
            label={t('Flags')}
            multiple
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
      </Grid>
    </ContainerWithBorder>
  );
};
