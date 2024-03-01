import { Grid, MenuItem } from '@mui/material';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useCashPlanVerificationStatusChoicesQuery } from '@generated/graphql';
import { DatePickerFilter } from '@components/core/DatePickerFilter';
import { SearchTextField } from '@components/core/SearchTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import { createHandleApplyFilterChange } from '@utils/utils';
import { FiltersSection } from '@components/core/FiltersSection';

interface PaymentVerificationFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const PaymentVerificationFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: PaymentVerificationFiltersProps): React.ReactElement => {
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

  const { data: statusChoicesData } =
    useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) {
    return null;
  }

  return (
    <FiltersSection
      applyHandler={handleApplyFilter}
      clearHandler={handleClearFilter}
    >
      <Grid container alignItems="flex-start" spacing={3}>
        <Grid item xs={3}>
          <div style={{ position: 'relative', bottom: '8px' }}>
            <SearchTextField
              value={filter.search}
              data-cy="filter-search"
              label="Payment Plan ID"
              onChange={(e) => handleFilterChange('search', e.target.value)}
              fullWidth
            />
          </div>
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('verificationStatus', e.target.value)
            }
            label="Status"
            multiple
            fullWidth
            data-cy="filter-status"
            value={filter.verificationStatus}
          >
            {statusChoicesData.cashPlanVerificationStatusChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <div style={{ position: 'relative', bottom: '8px' }}>
            <SearchTextField
              value={filter.serviceProvider}
              data-cy="filter-fsp"
              label="FSP"
              fullWidth
              onChange={(e) =>
                handleFilterChange('serviceProvider', e.target.value)
              }
            />
          </div>
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('deliveryType', e.target.value)}
            label="Delivery Mechanism"
            data-cy="filter-Modality"
            multiple
            value={filter.deliveryType}
            fullWidth
            icon={<MonetizationOnIcon />}
          >
            {statusChoicesData.paymentRecordDeliveryTypeChoices.map((item) => (
              <MenuItem key={item.name} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            label="Start Date"
            fullWidth
            data-cy="filter-start-date"
            onChange={(date) => handleFilterChange('startDate', date)}
            value={filter.startDate}
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            label="End Date"
            fullWidth
            data-cy="filter-end-date"
            onChange={(date) => handleFilterChange('endDate', date)}
            value={filter.endDate}
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
};
