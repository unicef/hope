import { Grid, MenuItem } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ContainerWithBorder } from '../../../../components/core/ContainerWithBorder';
import { DatePickerFilter } from '../../../../components/core/DatePickerFilter';
import { NumberTextField } from '../../../../components/core/NumberTextField';
import { SearchTextField } from '../../../../components/core/SearchTextField';
import { SelectFilter } from '../../../../components/core/SelectFilter';
import {
  usePaymentPlanStatusChoicesQueryQuery,
  AllPaymentPlansForTableQueryVariables,
} from '../../../../__generated__/graphql';

export type FilterProps = Pick<
  AllPaymentPlansForTableQueryVariables,
  | 'search'
  | 'status'
  | 'totalEntitledQuantityFrom'
  | 'totalEntitledQuantityTo'
  | 'dispersionStartDate'
  | 'dispersionEndDate'
>;

interface PaymentPlansFiltersProps {
  onFilterChange: (filter: FilterProps) => void;
  filter: FilterProps;
}

export function PaymentPlansFilters({
  onFilterChange,
  filter,
}: PaymentPlansFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name: string): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  const { data: statusChoicesData } = usePaymentPlanStatusChoicesQueryQuery();

  if (!statusChoicesData) {
    return null;
  }

  return (
    <ContainerWithBorder>
      <Grid container spacing={4}>
        <Grid item container spacing={4} xs={6} alignItems='flex-end'>
          <Grid item xs={8}>
            <SearchTextField
              label={t('Search')}
              value={filter.search}
              fullWidth
              onChange={(e) => handleFilterChange(e, 'search')}
            />
          </Grid>
          <Grid item xs={4}>
            <SelectFilter
              onChange={(e: unknown) => handleFilterChange(e, 'status')}
              variant='outlined'
              label={t('Status')}
              multiple
              value={filter.status || []}
              fullWidth
              autoWidth
            >
              {statusChoicesData.paymentPlanStatusChoices.map((item) => {
                return (
                  <MenuItem key={item.value} value={item.value}>
                    {item.name}
                  </MenuItem>
                );
              })}
            </SelectFilter>
          </Grid>
        </Grid>
        <Grid item container spacing={2} xs={3} alignItems='flex-end'>
          <Grid item xs={6}>
            <NumberTextField
              id='totalEntitledQuantityFromFilter'
              topLabel={t('Entitled Quantity')}
              value={filter.totalEntitledQuantityFrom}
              placeholder={t('From')}
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  totalEntitledQuantityFrom: e.target.value || undefined,
                })
              }
            />
          </Grid>
          <Grid item xs={6}>
            <NumberTextField
              id='totalEntitledQuantityToFilter'
              value={filter.totalEntitledQuantityTo}
              placeholder={t('To')}
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  totalEntitledQuantityTo: e.target.value || undefined,
                })
              }
              error={
                filter.totalEntitledQuantityFrom &&
                filter.totalEntitledQuantityTo &&
                filter.totalEntitledQuantityFrom >
                  filter.totalEntitledQuantityTo
              }
            />
          </Grid>
        </Grid>
        <Grid item container spacing={2} xs={3} alignItems='flex-end'>
          <Grid item xs={6}>
            <DatePickerFilter
              topLabel={t('Dispersion Date')}
              label={t('From')}
              onChange={(date) => {
                if (
                  filter.dispersionEndDate &&
                  date.isAfter(filter.dispersionEndDate)
                ) {
                  onFilterChange({
                    ...filter,
                    dispersionStartDate: date
                      ? date.format('YYYY-MM-DD')
                      : undefined,
                    dispersionEndDate: undefined,
                  });
                } else {
                  onFilterChange({
                    ...filter,
                    dispersionStartDate: date
                      ? date.format('YYYY-MM-DD')
                      : undefined,
                  });
                }
              }}
              value={filter.dispersionStartDate || undefined}
            />
          </Grid>
          <Grid item xs={6}>
            <DatePickerFilter
              label={t('To')}
              onChange={(date) =>
                onFilterChange({
                  ...filter,
                  dispersionEndDate: date
                    ? date.format('YYYY-MM-DD')
                    : undefined,
                })
              }
              value={filter.dispersionEndDate || undefined}
              minDate={filter.dispersionStartDate || undefined}
              minDateMessage={<span />}
            />
          </Grid>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
