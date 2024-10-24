import { Grid, MenuItem } from '@mui/material';
import { Group, Person } from '@mui/icons-material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { TargetPopulationStatus } from '@generated/graphql';
import {
  createHandleApplyFilterChange,
  targetPopulationStatusMapping,
} from '@utils/utils';
import { DatePickerFilter } from '@core/DatePickerFilter';
import { FiltersSection } from '@core/FiltersSection';
import { NumberTextField } from '@core/NumberTextField';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';

interface LookUpTargetPopulationFiltersCommunicationProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export function LookUpTargetPopulationFiltersCommunication({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: LookUpTargetPopulationFiltersCommunicationProps): React.ReactElement {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const isAccountability = location.pathname.includes('accountability');

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

  const preparedStatusChoices = isAccountability
    ? Object.values(TargetPopulationStatus).filter((key) => key !== 'OPEN')
    : Object.values(TargetPopulationStatus);

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
      isOnPaper={false}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.name}
            onChange={(e) => handleFilterChange('name', e.target.value)}
            data-cy="filters-search"
            fullWidth
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            value={filter.status}
            label={t('Status')}
            icon={<Person />}
            fullWidth
            data-cy="filters-status"
          >
            {preparedStatusChoices.sort().map((key) => (
              <MenuItem key={key} value={key}>
                {targetPopulationStatusMapping(key)}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            topLabel={t('Num. of Recipients')}
            value={filter.totalHouseholdsCountWithValidPhoneNoMin}
            placeholder={t('From')}
            onChange={(e) =>
              handleFilterChange(
                'totalHouseholdsCountWithValidPhoneNoMin',
                e.target.value,
              )
            }
            icon={<Group />}
            data-cy="filters-total-households-count-min"
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            value={filter.totalHouseholdsCountWithValidPhoneNoMax}
            placeholder={t('To')}
            onChange={(e) =>
              handleFilterChange(
                'totalHouseholdsCountWithValidPhoneNoMax',
                e.target.value,
              )
            }
            icon={<Group />}
            data-cy="filters-total-households-count-max"
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            topLabel={t('Date Created')}
            placeholder={t('From')}
            onChange={(date) => handleFilterChange('createdAtRangeMin', date)}
            value={filter.createdAtRangeMin}
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) => handleFilterChange('createdAtRangeMax', date)}
            value={filter.createdAtRangeMax}
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
