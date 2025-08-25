import { DatePickerFilter } from '@components/core/DatePickerFilter';
import { FiltersSection } from '@components/core/FiltersSection';
import { NumberTextField } from '@components/core/NumberTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import { Grid2 as Grid, MenuItem } from '@mui/material';
import { RdiAutocompleteRestFilter } from '@shared/autocompletes/RdiAutocompleteRestFilter';
import { AdminAreaAutocompleteMultipleRestFilter } from '@shared/autocompletes/rest/AdminAreaAutocompleteMultipleRestFilter';
import { TargetPopulationAutocompleteRestFilter } from '@shared/autocompletes/rest/TargetPopulationAutocompleteRestFilter';
import { t } from 'i18next';
import React, { FC } from 'react';

interface FilterIndividualsOnlineProps {
  filter;
  setFilter: (filter) => void;
  isOnPaper: boolean;
}

export const FilterIndividualsOnline: FC<FilterIndividualsOnlineProps> = ({
  filter,
  setFilter,

  isOnPaper = true,
}) => {
  const handleStateFilterChange = (name, value) => {
    setFilter((prevFilter) => ({
      ...prevFilter,
      [name]: value,
    }));
  };

  return (
    <FiltersSection isOnPaper={isOnPaper} withApplyClearButtons={false}>
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid size={{ xs: 3 }}>
          <RdiAutocompleteRestFilter
            value={filter.registrationDataImportId}
            onChange={(selectedItem) =>
              handleStateFilterChange('registrationDataImportId', selectedItem)
            }
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <TargetPopulationAutocompleteRestFilter
            value={filter.targetPopulationId}
            onChange={(selectedItem) =>
              handleStateFilterChange('targetPopulationId', selectedItem)
            }
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) => handleStateFilterChange('gender', e.target.value)}
            label={t('Gender')}
            value={filter.gender}
            data-cy="ind-filters-gender"
          >
            <MenuItem key="male" value="MALE">
              {t('Male')}
            </MenuItem>
            <MenuItem key="female" value="FEMALE">
              {t('Female')}
            </MenuItem>
            <MenuItem key="other" value="OTHER">
              {t('Other')}
            </MenuItem>
            <MenuItem key="not_collected" value="NOT_COLLECTED">
              {t('Not Collected')}
            </MenuItem>
            <MenuItem key="not_answered" value="NOT_ANSWERED">
              {t('Not Answered')}
            </MenuItem>
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <NumberTextField
            topLabel={t('Age')}
            value={filter.ageFrom}
            placeholder={t('From')}
            fullWidth
            onChange={(e) => handleStateFilterChange('ageFrom', e.target.value)}
            data-cy="hh-filters-age-from"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <NumberTextField
            value={filter.ageTo}
            placeholder={t('To')}
            fullWidth
            onChange={(e) => handleStateFilterChange('ageTo', e.target.value)}
            data-cy="hh-filters-age-to"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            topLabel={t('Registration Date')}
            placeholder={t('From')}
            onChange={(date) =>
              handleStateFilterChange('registrationDateFrom', date)
            }
            value={filter.registrationDateFrom}
            dataCy="ind-filters-reg-date-from"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) =>
              handleStateFilterChange('registrationDateTo', date)
            }
            value={filter.registrationDateTo}
            dataCy="ind-filters-reg-date-to"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) =>
              handleStateFilterChange('hasGrievanceTicket', e.target.value)
            }
            label={t('Has a Grievance Ticket')}
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
        <Grid size={{ xs: 3 }}>
          <AdminAreaAutocompleteMultipleRestFilter
            value={filter.admin1 || []}
            onChange={(_, option) => {
              handleStateFilterChange('admin1', option);
            }}
            level={1}
            dataCy="filter-admin1"
            disabled={filter.admin2?.length > 0}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <AdminAreaAutocompleteMultipleRestFilter
            value={filter.admin2 || []}
            onChange={(_, option) => {
              handleStateFilterChange('admin2', option);
            }}
            level={2}
            dataCy="filter-admin2"
            disabled={filter.admin1?.length > 0}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) =>
              handleStateFilterChange('receivedAssistance', e.target.value)
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
      </Grid>
    </FiltersSection>
  );
};
