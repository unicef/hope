import { DatePickerFilter } from '@components/core/DatePickerFilter';
import { FiltersSection } from '@components/core/FiltersSection';
import { SearchTextField } from '@components/core/SearchTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import withErrorBoundary from '@components/core/withErrorBoundary';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import { Grid2 as Grid, MenuItem } from '@mui/material';
import { Choice } from '@restgenerated/models/Choice';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { createHandleApplyFilterChange } from '@utils/utils';
import { ReactElement } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface PaymentVerificationFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
const PaymentVerificationFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: PaymentVerificationFiltersProps): ReactElement => {
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

  const { data: statusChoicesData } = useQuery<Array<Choice>>({
    queryKey: ['choicesPaymentVerificationSummaryStatusList'],
    queryFn: () =>
      RestService.restChoicesPaymentVerificationSummaryStatusList(),
  });
  const { data: deliveryTypeChoicesData } = useQuery<Array<Choice>>({
    queryKey: ['choicesPaymentRecordDeliveryTypeList'],
    queryFn: () => RestService.restChoicesPaymentRecordDeliveryTypeList(),
  });

  if (!statusChoicesData || !deliveryTypeChoicesData) {
    return null;
  }

  return (
    <FiltersSection
      applyHandler={handleApplyFilter}
      clearHandler={handleClearFilter}
    >
      <Grid container alignItems="flex-start" spacing={3}>
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            value={filter.search}
            data-cy="filter-search"
            label="Payment Plan ID"
            onChange={(e) => handleFilterChange('search', e.target.value)}
            fullWidth
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('paymentVerificationSummaryStatus', e.target.value)
            }
            label="Status"
            multiple
            fullWidth
            data-cy="filter-status"
            value={filter.paymentVerificationSummaryStatus}
          >
            {statusChoicesData.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            value={filter.serviceProvider}
            data-cy="filter-fsp"
            label="FSP"
            fullWidth
            onChange={(e) =>
              handleFilterChange('serviceProvider', e.target.value)
            }
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('deliveryTypes', e.target.value)
            }
            label="Delivery Mechanism"
            data-cy="filter-Modality"
            multiple
            value={filter.deliveryTypes}
            fullWidth
            icon={<MonetizationOnIcon />}
          >
            {deliveryTypeChoicesData.map((item) => (
              <MenuItem key={item.name} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            label="Start Date"
            fullWidth
            dataCy="filter-start-date"
            onChange={(date) => handleFilterChange('startDate', date)}
            value={filter.startDate}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            label="End Date"
            fullWidth
            dataCy="filter-end-date"
            onChange={(date) => handleFilterChange('endDate', date)}
            value={filter.endDate}
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
};

export default withErrorBoundary(
  PaymentVerificationFilters,
  'PaymentVerificationFilters',
);
