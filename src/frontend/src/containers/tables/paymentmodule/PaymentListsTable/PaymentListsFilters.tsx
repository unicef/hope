import { MenuItem } from '@mui/material';
import moment from 'moment';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { PaymentListStatusEnum } from '@restgenerated/models/PaymentListStatusEnum';
import { DatePickerFilter } from '@components/core/DatePickerFilter';
import { FiltersSection } from '@components/core/FiltersSection';
import { NumberTextField } from '@components/core/NumberTextField';
import { SearchTextField } from '@components/core/SearchTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import { createHandleApplyFilterChange, formatFigure } from '@utils/utils';
import type { ReactElement } from 'react';
import type { PaymentList } from '@restgenerated/models/PaymentList';
import type { Choice } from '@restgenerated/models/Choice';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { useQuery } from '@tanstack/react-query';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

export type FilterProps = Partial<PaymentList>;

interface PaymentListsFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

export const allowedStatusChoices = [
  PaymentListStatusEnum.ACCEPTED,
  PaymentListStatusEnum.DRAFT,
  PaymentListStatusEnum.FINISHED,
  PaymentListStatusEnum.IN_APPROVAL,
  PaymentListStatusEnum.IN_AUTHORIZATION,
  PaymentListStatusEnum.IN_REVIEW,
  PaymentListStatusEnum.LOCKED,
  PaymentListStatusEnum.LOCKED_FSP,
  PaymentListStatusEnum.OPEN,
  PaymentListStatusEnum.STEFICON_COMPLETED,
  PaymentListStatusEnum.STEFICON_ERROR,
  PaymentListStatusEnum.STEFICON_RUN,
  PaymentListStatusEnum.STEFICON_WAIT,
];

export function PaymentListsFilters({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: PaymentListsFiltersProps): ReactElement {
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
    queryKey: restQueryKey(RestService.restChoicesPaymentListStatusList),
    queryFn: () => RestService.restChoicesPaymentListStatusList(),
  });

  const preparedStatusChoices =
    [...(statusChoicesData || [])]?.filter((el) =>
      allowedStatusChoices.includes(el.value as any),
    ) || [];

  const { data: planTypeChoicesData } = useQuery<Array<Choice>>({
    queryKey: restQueryKey(RestService.restChoicesPaymentListTypeList),
    queryFn: () => RestService.restChoicesPaymentListTypeList(),
  });

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <ResponsiveGridContainer
        spacing={3}
        sx={{
          alignItems: 'flex-end',
        }}
      >
        <ResponsiveGrid size="quarter">
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            fullWidth
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filter-search"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('planType', e.target.value || null)
            }
            label={t('Plan Type')}
            value={filter.planType ?? ''}
            fullWidth
          >
            {(planTypeChoicesData || []).map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </FiltersSection>
  );
}
