import { ClearApplyButtons } from '@core/ClearApplyButtons';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { createHandleApplyFilterChange } from '@utils/utils';
import React from 'react';
import Grid from '@mui/material/Grid';
import { ContainerWithBorder } from '@core/ContainerWithBorder';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { MenuItem } from '@mui/material';
import { NumberTextField } from '@core/NumberTextField';
import { DatePickerFilter } from '@core/DatePickerFilter';
import moment from 'moment/moment';

interface ProgramCyclesFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

const programCycleStatuses = [
  { value: 'ACTIVE', name: 'Active' },
  { value: 'DRAFT', name: 'Draft' },
  { value: 'FINISHED', name: 'Finished' },
];

export const ProgramCyclesFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: ProgramCyclesFiltersProps) => {
  const { t } = useTranslation();
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
    <ContainerWithBorder>
      <Grid container spacing={3} alignItems="flex-end">
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            fullWidth
            onChange={(e) => handleFilterChange('search', e.target.value)}
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            variant="outlined"
            label={t('Status')}
            multiple
            value={filter.status}
            fullWidth
          >
            {programCycleStatuses.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            id="totalEntitledQuantityUsdFromFilter"
            topLabel={t('Total Entitled Quantity')}
            value={filter.totalEntitledQuantityUsdFrom}
            placeholder={t('From')}
            onChange={(e) =>
              handleFilterChange('totalEntitledQuantityUsdFrom', e.target.value)
            }
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            id="totalEntitledQuantityUsdToFilter"
            value={filter.totalEntitledQuantityUsdTo}
            placeholder={t('To')}
            onChange={(e) =>
              handleFilterChange('totalEntitledQuantityUsdTo', e.target.value)
            }
            error={
              filter.totalEntitledQuantityUsdFrom &&
              filter.totalEntitledQuantityUsdTo &&
              filter.totalEntitledQuantityUsdFrom >
                filter.totalEntitledQuantityUsdTo
            }
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            topLabel="Date"
            onChange={(date) =>
              handleFilterChange(
                'startDate',
                date ? moment(date).format('YYYY-MM-DD') : '',
              )
            }
            value={filter.startDate}
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            onChange={(date) =>
              handleFilterChange(
                'endDate',
                date ? moment(date).format('YYYY-MM-DD') : '',
              )
            }
            value={filter.endDate}
          />
        </Grid>
      </Grid>
      <ClearApplyButtons
        clearHandler={handleClearFilter}
        applyHandler={handleApplyFilter}
      />
    </ContainerWithBorder>
  );
};
