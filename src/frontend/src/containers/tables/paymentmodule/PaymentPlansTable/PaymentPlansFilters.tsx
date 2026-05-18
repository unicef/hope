import { Grid, MenuItem } from '@mui/material';
import moment from 'moment';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { DatePickerFilter } from '@components/core/DatePickerFilter';
import { FiltersSection } from '@components/core/FiltersSection';
import { NumberTextField } from '@components/core/NumberTextField';
import { SearchTextField } from '@components/core/SearchTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import { createHandleApplyFilterChange, formatFigure } from '@utils/utils';
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
  PaymentPlanStatusEnum.ACCEPTED,
  PaymentPlanStatusEnum.DRAFT,
  PaymentPlanStatusEnum.FINISHED,
  PaymentPlanStatusEnum.IN_APPROVAL,
  PaymentPlanStatusEnum.IN_AUTHORIZATION,
  PaymentPlanStatusEnum.IN_REVIEW,
  PaymentPlanStatusEnum.LOCKED,
  PaymentPlanStatusEnum.LOCKED_FSP,
  PaymentPlanStatusEnum.OPEN,
  PaymentPlanStatusEnum.PREPARING,
  PaymentPlanStatusEnum.PROCESSING,
  PaymentPlanStatusEnum.STEFICON_COMPLETED,
  PaymentPlanStatusEnum.STEFICON_ERROR,
  PaymentPlanStatusEnum.STEFICON_RUN,
  PaymentPlanStatusEnum.STEFICON_WAIT,
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
        <Grid size={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            fullWidth
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filter-search"
          />
        </Grid>
        <Grid size={3}>
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
        <Grid size={3}>
          <NumberTextField
            id="totalEntitledQuantityFromFilter"
            topLabel={t('Entitled Quantity')}
            value={formatFigure(filter.totalEntitledQuantityUsdFrom)}
            placeholder={t('From')}
            onChange={(e) =>
              handleFilterChange('totalEntitledQuantityUsdFrom', e.target.value)
            }
            data-cy="filters-total-entitled-quantity-from"
          />
        </Grid>
        <Grid size={3}>
          <NumberTextField
            id="totalEntitledQuantityToFilter"
            value={formatFigure(filter.totalEntitledQuantityUsdTo)}
            placeholder={t('To')}
            onChange={(e) =>
              handleFilterChange('totalEntitledQuantityUsdTo', e.target.value)
            }
            error={Boolean(
              filter.totalEntitledQuantityFrom &&
              filter.totalEntitledQuantityTo &&
              filter.totalEntitledQuantityFrom > filter.totalEntitledQuantityTo,
            )}
            data-cy="filters-total-entitled-quantity-to"
          />
        </Grid>
        <Grid size={3}>
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
        <Grid size={3}>
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
        <Grid size={3}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('planType', e.target.value || null)
            }
            label={t('Plan Type')}
            value={filter.planType ?? ''}
            fullWidth
          >
            <MenuItem value="FOLLOW_UP">{t('Follow Up')}</MenuItem>
            <MenuItem value="TOP_UP">{t('Top Up')}</MenuItem>
          </SelectFilter>
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
