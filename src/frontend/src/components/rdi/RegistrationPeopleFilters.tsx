import { Grid, MenuItem } from '@mui/material';
import GroupIcon from '@mui/icons-material/Group';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useRegistrationChoicesQuery } from '@generated/graphql';
import { AssigneeAutocomplete } from '@shared/autocompletes/AssigneeAutocomplete';
import { createHandleApplyFilterChange } from '@utils/utils';
import { DatePickerFilter } from '@core/DatePickerFilter';
import { NumberTextField } from '@core/NumberTextField';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { FiltersSection } from '@core/FiltersSection';

interface RegistrationFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

export const RegistrationPeopleFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: RegistrationFiltersProps): React.ReactElement => {
  const navigate = useNavigate();
  const location = useLocation();

  const { handleFilterChange, applyFilterChanges, clearFilter } =
    createHandleApplyFilterChange(
      initialFilter,
      navigate,
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

  const { t } = useTranslation();
  const { data: registrationChoicesData } = useRegistrationChoicesQuery();
  if (!registrationChoicesData) {
    return null;
  }

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid item xs={4}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filter-search"
          />
        </Grid>
        <Grid item xs={4}>
          <AssigneeAutocomplete
            name="importedBy"
            label={t('Imported By')}
            filter={filter}
            value={filter.importedBy}
            data-cy="filter-imported-by"
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </Grid>
        <Grid item xs={4}>
          <SelectFilter
            value={filter.status}
            label={t('Status')}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            data-cy="filter-status"
          >
            {registrationChoicesData.registrationDataStatusChoices.map(
              (item) => (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              ),
            )}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            id="minFilter"
            topLabel={t('Num. of People')}
            value={filter.sizeMin}
            placeholder="From"
            icon={<GroupIcon />}
            onChange={(e) => handleFilterChange('sizeMin', e.target.value)}
            data-cy="filter-size-min"
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            id="maxFilter"
            value={filter.sizeMax}
            placeholder="To"
            icon={<GroupIcon />}
            onChange={(e) => handleFilterChange('sizeMax', e.target.value)}
            data-cy="filter-size-max"
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            topLabel={t('Import Date')}
            placeholder={t('From')}
            onChange={(date) => handleFilterChange('importDateRangeMin', date)}
            value={filter.importDateRangeMin}
            dataCy="filter-import-date-range-min"
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) => handleFilterChange('importDateRangeMax', date)}
            value={filter.importDateRangeMax}
            dataCy="filter-import-date-range-max"
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
};
