import {
  Box,
  Checkbox,
  FormControlLabel,
  Grid2 as Grid,
  MenuItem,
} from '@mui/material';
import moment from 'moment';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { PaymentPlanStatus } from '@generated/graphql';
import { DatePickerFilter } from '@components/core/DatePickerFilter';
import { FiltersSection } from '@components/core/FiltersSection';
import { NumberTextField } from '@components/core/NumberTextField';
import { SearchTextField } from '@components/core/SearchTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import { createHandleApplyFilterChange } from '@utils/utils';
import { ReactElement } from 'react';
import { PaymentPlan } from '@restgenerated/models/PaymentPlan';
import { Choice } from '@restgenerated/models/Choice';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

export type FilterProps = Partial<PaymentPlan>;

interface PaymentPlansFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

export const allowedStatusChoices = [
  //TODO: add pp status choices
  PaymentPlanStatus.Accepted,
  PaymentPlanStatus.Draft,
  PaymentPlanStatus.Finished,
  PaymentPlanStatus.InApproval,
  PaymentPlanStatus.InAuthorization,
  PaymentPlanStatus.InReview,
  PaymentPlanStatus.Locked,
  PaymentPlanStatus.LockedFsp,
  PaymentPlanStatus.Open,
  PaymentPlanStatus.Preparing,
  PaymentPlanStatus.Processing,
  PaymentPlanStatus.SteficonCompleted,
  PaymentPlanStatus.SteficonError,
  PaymentPlanStatus.SteficonRun,
  PaymentPlanStatus.SteficonWait,
];

export function PaymentPlansFilters({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: PaymentPlansFiltersProps): ReactElement {
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
  const { data: statusChoicesData } = useQuery<Array<Choice>>({
    queryKey: ['choicesPaymentVerificationPlanStatusList'],
    queryFn: () => RestService.restChoicesPaymentPlanStatusList(),
  });

  const preparedStatusChoices =
    [...(statusChoicesData || [])]?.filter((el) =>
      allowedStatusChoices.includes(el.value as any),
    ) || [];

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <Grid container spacing={3} alignItems="flex-end">
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            fullWidth
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filter-search"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            variant="outlined"
            label={t('Status')}
            multiple
            value={filter.status}
            fullWidth
          >
            {preparedStatusChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <NumberTextField
            id="totalEntitledQuantityFromFilter"
            topLabel={t('Entitled Quantity')}
            value={filter.totalEntitledQuantityFrom}
            placeholder={t('From')}
            onChange={(e) =>
              handleFilterChange('totalEntitledQuantityFrom', e.target.value)
            }
            data-cy="filters-total-entitled-quantity-from"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <NumberTextField
            id="totalEntitledQuantityToFilter"
            value={filter.totalEntitledQuantityTo}
            placeholder={t('To')}
            onChange={(e) =>
              handleFilterChange('totalEntitledQuantityTo', e.target.value)
            }
            error={Boolean(
              filter.totalEntitledQuantityFrom &&
                filter.totalEntitledQuantityTo &&
                filter.totalEntitledQuantityFrom >
                  filter.totalEntitledQuantityTo,
            )}
            data-cy="filters-total-entitled-quantity-to"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            topLabel={t('Dispersion Date')}
            placeholder={t('From')}
            onChange={(date) => {
              if (
                filter.dispersionEndDate &&
                moment(date).isAfter(filter.dispersionEndDate)
              ) {
                handleFilterChange(
                  'dispersionStartDate',
                  date ? moment(date).format('YYYY-MM-DD') : '',
                );
                handleFilterChange('dispersionEndDate', '');
              } else {
                handleFilterChange(
                  'dispersionStartDate',
                  date ? moment(date).format('YYYY-MM-DD') : '',
                );
              }
            }}
            value={filter.dispersionStartDate}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) =>
              handleFilterChange(
                'dispersionEndDate',
                date ? moment(date).format('YYYY-MM-DD') : '',
              )
            }
            value={filter.dispersionEndDate}
            minDate={filter.dispersionStartDate}
            minDateMessage={<span />}
          />
        </Grid>
        <Grid size={{ xs: 12 }}>
          <Box ml={2}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={Boolean(filter.isFollowUp)}
                  value={filter.isFollowUp}
                  color="primary"
                  onChange={(e) => {
                    if (e.target.checked) {
                      handleFilterChange('isFollowUp', true);
                    } else {
                      handleFilterChange('isFollowUp', false);
                    }
                  }}
                />
              }
              label={t('Show only Follow-up plans')}
            />
          </Box>
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
