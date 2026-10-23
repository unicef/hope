import { DatePickerFilter } from '@components/core/DatePickerFilter';
import { FiltersSection } from '@components/core/FiltersSection';
import { SearchTextField } from '@components/core/SearchTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import withErrorBoundary from '@components/core/withErrorBoundary';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import { MenuItem } from '@mui/material';
import type { Choice } from '@restgenerated/models/Choice';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { useQuery } from '@tanstack/react-query';
import { createHandleApplyFilterChange } from '@utils/utils';
import type { ReactElement } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

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
    queryKey: restQueryKey(
      RestService.restChoicesPaymentVerificationSummaryStatusList,
    ),
    queryFn: () =>
      RestService.restChoicesPaymentVerificationSummaryStatusList(),
  });
  const { data: deliveryTypeChoicesData } = useQuery<Array<Choice>>({
    queryKey: restQueryKey(
      RestService.restChoicesPaymentRecordDeliveryTypeList,
    ),
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
      <ResponsiveGridContainer
        spacing={3}
        sx={{
          alignItems: 'flex-start',
        }}
      >
        <ResponsiveGrid size="quarter">
          <SearchTextField
            value={filter.search}
            data-cy="filter-search"
            label="Payment Plan ID"
            onChange={(e) => handleFilterChange('search', e.target.value)}
            fullWidth
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) =>
              handleFilterChange(
                'paymentVerificationSummaryStatus',
                e.target.value,
              )
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SearchTextField
            value={filter.serviceProvider}
            data-cy="filter-fsp"
            label="FSP"
            fullWidth
            onChange={(e) =>
              handleFilterChange('serviceProvider', e.target.value)
            }
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <DatePickerFilter
            label="Start Date"
            fullWidth
            dataCy="filter-start-date"
            onChange={(date) => handleFilterChange('startDate', date)}
            value={filter.startDate}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <DatePickerFilter
            label="End Date"
            fullWidth
            dataCy="filter-end-date"
            onChange={(date) => handleFilterChange('endDate', date)}
            value={filter.endDate}
          />
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </FiltersSection>
  );
};

export default withErrorBoundary(
  PaymentVerificationFilters,
  'PaymentVerificationFilters',
);
