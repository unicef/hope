import { Grid, MenuItem } from '@material-ui/core';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ContainerWithBorder } from '../../../../components/core/ContainerWithBorder';
import { DatePickerFilter } from '../../../../components/core/DatePickerFilter';
import { NumberTextField } from '../../../../components/core/NumberTextField';
import { SearchTextField } from '../../../../components/core/SearchTextField';
import { SelectFilter } from '../../../../components/core/SelectFilter';
import { useCashPlanVerificationStatusChoicesQuery } from '../../../../__generated__/graphql';

export interface FilterProps {
  search: string;
  dispersionDate: string;
  status: string;
  entitlement: {
      min: number;
      max: number;
  };
}

interface PaymentPlansFiltersProps {
  onFilterChange: (filter: FilterProps) => void;
  filter: FilterProps;
}
export function PaymentPlansFilters({
  onFilterChange,
  filter,
}: PaymentPlansFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  const {
    data: statusChoicesData,
  } = useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) {
    return null;
  }

  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange(e, 'search')}
          />
        </Grid>
        <Grid item>
          <DatePickerFilter
            label={t('Dispersion Date')}
            onChange={(date: string) =>
              onFilterChange({
                ...filter,
                dispersionDate: moment(date)
                  .startOf('day')
                  .toISOString(),
              })
            }
            value={filter.dispersionDate || null}
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e: unknown) => handleFilterChange(e, 'status')}
            variant='outlined'
            label={t('Status')}
            multiple
            value={filter.status || []}
          >
            {statusChoicesData.cashPlanVerificationStatusChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item>
          <NumberTextField
            id='minFilter'
            topLabel={t('Entitled Quantity')}
            value={filter.entitlement.min}
            placeholder={t('From')}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                entitlement: {
                  ...filter.entitlement,
                  min: e.target.value || undefined,
                },
              })
            }
          />
        </Grid>
        <Grid item>
          <NumberTextField
            id='maxFilter'
            value={filter.entitlement.max}
            placeholder={t('To')}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                entitlement: {
                  ...filter.entitlement,
                  max: e.target.value || undefined,
                },
              })
            }
          />
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
