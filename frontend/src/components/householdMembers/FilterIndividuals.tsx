import { DatePickerFilter } from '@components/core/DatePickerFilter';
import { FiltersSection } from '@components/core/FiltersSection';
import { NumberTextField } from '@components/core/NumberTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import { Grid, MenuItem } from '@mui/material';
import { AdminAreaAutocomplete } from '@shared/autocompletes/AdminAreaAutocomplete';
import { RdiAutocomplete } from '@shared/autocompletes/RdiAutocomplete';
import { TargetPopulationAutocomplete } from '@shared/autocompletes/TargetPopulationAutocomplete';
import { createHandleApplyFilterChange } from '@utils/utils';
import { t } from 'i18next';
import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface FilterIndividualsProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

export const FilterIndividuals: React.FC<FilterIndividualsProps> = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}) => {
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

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid item xs={3}>
          <RdiAutocomplete
            filter={filter}
            name="registrationDataImport"
            value={filter.registrationDataImport}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            setFilter={setFilter}
          />
        </Grid>
        <Grid item xs={3}>
          <TargetPopulationAutocomplete
            name="targetPopulation"
            value={filter.targetPopulation}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </Grid>
        <Grid item xs={2}>
          <SelectFilter
            onChange={(e) => handleFilterChange('sex', e.target.value)}
            label={t('Gender')}
            value={filter.sex}
            data-cy="ind-filters-gender"
          >
            <MenuItem key="male" value="MALE">
              {t('Male')}
            </MenuItem>
            <MenuItem key="female" value="FEMALE">
              {t('Female')}
            </MenuItem>
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            topLabel={t('Age')}
            value={filter.ageMin}
            placeholder={t('From')}
            fullWidth
            onChange={(e) => handleFilterChange('ageMin', e.target.value)}
            data-cy="hh-filters-age-from"
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            value={filter.ageMax}
            placeholder={t('To')}
            fullWidth
            onChange={(e) => handleFilterChange('ageMax', e.target.value)}
            data-cy="hh-filters-age-to"
          />
        </Grid>
        <Grid item xs={2}>
          <DatePickerFilter
            topLabel={t('Registration Date')}
            placeholder={t('From')}
            onChange={(date) =>
              handleFilterChange('lastRegistrationDateMin', date)
            }
            value={filter.lastRegistrationDateMin}
            dataCy="ind-filters-reg-date-from"
          />
        </Grid>
        <Grid item xs={2}>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) =>
              handleFilterChange('lastRegistrationDateMax', date)
            }
            value={filter.lastRegistrationDateMax}
            dataCy="ind-filters-reg-date-to"
          />
        </Grid>
        <Grid item xs={2}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('hasGrievanceTicket', e.target.value)
            }
            label={t('Have a Grievance Ticket')}
            value={filter.hasGrievanceTicket}
            data-cy="ind-filters-grievance-ticket"
          >
            <MenuItem key="yes" value="YES">
              {t('Yes')}
            </MenuItem>
            <MenuItem key="no" value="NO">
              {t('No')}
            </MenuItem>
          </SelectFilter>
        </Grid>
        {/* //TODO MS: possibly replace with new component with checkboxes in filters options */}
        <Grid item xs={3}>
          <AdminAreaAutocomplete
            name="administrativeArea1"
            level={1}
            value={filter.administrativeArea}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy="filter-administrative-area"
          />
        </Grid>
        <Grid item xs={3}>
          <AdminAreaAutocomplete
            name="administrativeArea2"
            multiple
            level={2}
            value={filter.administrativeArea}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy="filter-administrative-area"
          />
        </Grid>
      </Grid>
      <Grid item xs={2}>
        <SelectFilter
          onChange={(e) =>
            handleFilterChange('receivedAssistance', e.target.value)
          }
          label={t('Received Assistance')}
          value={filter.receivedAssistance}
          data-cy="ind-filters-received-assistance"
        >
          <MenuItem key="yes" value="YES">
            {t('Yes')}
          </MenuItem>
          <MenuItem key="no" value="NO">
            {t('No')}
          </MenuItem>
        </SelectFilter>
      </Grid>
    </FiltersSection>
  );
};
