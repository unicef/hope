import { Grid2 as Grid, MenuItem } from '@mui/material';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import { useLocation, useNavigate } from 'react-router-dom';
import { DatePickerFilter } from '@components/core/DatePickerFilter';
import { SearchTextField } from '@components/core/SearchTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import { createHandleApplyFilterChange } from '@utils/utils';
import { FiltersSection } from '@components/core/FiltersSection';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { useCashPlanVerificationStatusChoicesQuery } from '@generated/graphql';

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

  const { data: statusChoicesData } = useCashPlanVerificationStatusChoicesQuery(
    {
      fetchPolicy: 'cache-first',
    },
  );

  if (!statusChoicesData) {
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
            {statusChoicesData.paymentRecordDeliveryTypeChoices.map((item) => (
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
