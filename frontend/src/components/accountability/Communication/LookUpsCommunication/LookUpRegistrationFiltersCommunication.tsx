import { Grid } from '@mui/material';
import GroupIcon from '@mui/icons-material/Group';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { useRegistrationChoicesQuery } from '../../../../__generated__/graphql';
import { AssigneeAutocomplete } from '../../../../shared/autocompletes/AssigneeAutocomplete';
import { createHandleApplyFilterChange } from '../../../../utils/utils';
import { DatePickerFilter } from '../../../core/DatePickerFilter';
import { FiltersSection } from '../../../core/FiltersSection';
import { NumberTextField } from '../../../core/NumberTextField';
import { SearchTextField } from '../../../core/SearchTextField';

interface LookUpRegistrationFiltersCommunicationProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

export const LookUpRegistrationFiltersCommunication = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: LookUpRegistrationFiltersCommunicationProps): React.ReactElement => {
  const history = useHistory();
  const location = useLocation();

  const { handleFilterChange, applyFilterChanges, clearFilter } =
    createHandleApplyFilterChange(
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

  const { t } = useTranslation();
  const { data: registrationChoicesData } = useRegistrationChoicesQuery();
  if (!registrationChoicesData) {
    return null;
  }

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
      isOnPaper={false}
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
        <Grid item xs={3}>
          <NumberTextField
            topLabel={t('Num. of Recipients')}
            value={filter.totalHouseholdsCountWithValidPhoneNoMin}
            placeholder="From"
            icon={<GroupIcon />}
            onChange={(e) =>
              handleFilterChange(
                'totalHouseholdsCountWithValidPhoneNoMin',
                e.target.value,
              )
            }
            data-cy="filter-size-min"
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            value={filter.totalHouseholdsCountWithValidPhoneNoMax}
            placeholder="To"
            icon={<GroupIcon />}
            onChange={(e) =>
              handleFilterChange(
                'totalHouseholdsCountWithValidPhoneNoMax',
                e.target.value,
              )
            }
            data-cy="filter-size-max"
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            topLabel={t('Import Date')}
            placeholder={t('From')}
            onChange={(date) => handleFilterChange('importDateRangeMin', date)}
            value={filter.importDateRangeMin}
            data-cy="filter-import-date-range-min"
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) => handleFilterChange('importDateRangeMax', date)}
            value={filter.importDateRangeMax}
            data-cy="filter-import-date-range-max"
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
};
