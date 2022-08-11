import { Grid, MenuItem } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ContainerWithBorder } from '../../../../components/core/ContainerWithBorder';
import { DatePickerFilter } from '../../../../components/core/DatePickerFilter';
import { NumberTextField } from '../../../../components/core/NumberTextField';
import { SearchTextField } from '../../../../components/core/SearchTextField';
import { SelectFilter } from '../../../../components/core/SelectFilter';
import { usePaymentPlanStatusChoicesQueryQuery, AllPaymentPlansForTableQueryVariables } from '../../../../__generated__/graphql';

export type FilterProps = Pick<AllPaymentPlansForTableQueryVariables, 'search' | 'status' | 'totalEntitledQuantityFrom' | 'totalEntitledQuantityTo' | 'dispersionStartDate' | 'dispersionEndDate'>

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
  const {
    data: statusChoicesData,
  } = usePaymentPlanStatusChoicesQueryQuery();

  if (!statusChoicesData) {
    return null;
  }

  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={2}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange(e, 'search')}
          />
        </Grid>
        <Grid item xs={2}>
          <SelectFilter
            onChange={(e: unknown) => handleFilterChange(e, 'status')}
            variant='outlined'
            label={t('Status')}
            multiple
            value={filter.status || []}
            fullWidth
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
        <Grid item xs={2}>
          <DatePickerFilter
            topLabel={t('Dispersion Date Range')}
            label={t('From Date')}
            onChange={(date) => onFilterChange({ ...filter, dispersionStartDate: date ? date.format('YYYY-MM-DD') : null })}
            value={filter.dispersionStartDate || null}
            clearable
          />
        </Grid>
        <Grid item xs={2}>
          <DatePickerFilter
            label={t('To Date')}
            onChange={(date) => onFilterChange({ ...filter, dispersionEndDate: date ? date.format('YYYY-MM-DD') : null })}
            value={filter.dispersionEndDate || null}
            minDate={filter.dispersionStartDate || undefined}
            clearable
          />
        </Grid>
        <Grid item xs={2}>
          <NumberTextField
            id='totalEntitledQuantityFromFilter'
            topLabel={t('Entitled Quantity')}
            value={filter.totalEntitledQuantityFrom}
            placeholder={t('From')}
            onChange={(e) => onFilterChange({ ...filter, totalEntitledQuantityFrom: e.target.value || undefined })}
          />
        </Grid>
        <Grid item xs={2}>
          <NumberTextField
            id='totalEntitledQuantityToFilter'
            value={filter.totalEntitledQuantityTo}
            placeholder={t('To')}
            onChange={(e) => onFilterChange({ ...filter, totalEntitledQuantityTo: e.target.value || undefined })}
            error={filter.totalEntitledQuantityFrom && filter.totalEntitledQuantityTo && filter.totalEntitledQuantityFrom > filter.totalEntitledQuantityTo}
          />
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
