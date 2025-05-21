import GroupIcon from '@mui/icons-material/Group';
import { Grid2 as Grid } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { AssigneeAutocompleteRestFilter } from '@shared/autocompletes/AssigneeAutocompleteRestFilter';
import { createHandleApplyFilterChange } from '@utils/utils';
import { DatePickerFilter } from '@core/DatePickerFilter';
import { FiltersSection } from '@core/FiltersSection';
import { NumberTextField } from '@core/NumberTextField';
import { SearchTextField } from '@core/SearchTextField';
import { ReactElement } from 'react';

interface LookUpRegistrationFiltersCommunicationProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

export function LookUpRegistrationFiltersCommunication({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: LookUpRegistrationFiltersCommunicationProps): ReactElement {
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

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
      isOnPaper={false}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid size={{ xs: 4 }}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filter-search"
          />
        </Grid>
        <Grid size={{ xs: 4 }}>
          <AssigneeAutocompleteRestFilter
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
        <Grid size={{ xs: 3 }}>
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
        <Grid size={{ xs: 3 }}>
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
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            topLabel={t('Import Date')}
            placeholder={t('From')}
            onChange={(date) => handleFilterChange('importDateRangeMin', date)}
            value={filter.importDateRangeMin}
            dataCy="filter-import-date-range-min"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
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
}
