import {
  Box,
  Checkbox,
  FormControlLabel,
  Grid,
  MenuItem,
} from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import {
  AllPaymentPlansForTableQueryVariables,
  usePaymentPlanStatusChoicesQueryQuery,
} from '../../../../__generated__/graphql';
import { ClearApplyButtons } from '../../../../components/core/ClearApplyButtons';
import { ContainerWithBorder } from '../../../../components/core/ContainerWithBorder';
import { DatePickerFilter } from '../../../../components/core/DatePickerFilter';
import { FlexSelectFilter } from '../../../../components/core/FlexSelectFilter';
import { NumberTextField } from '../../../../components/core/NumberTextField';
import { SearchTextField } from '../../../../components/core/SearchTextField';
import { createHandleApplyFilterChange } from '../../../../utils/utils';

export type FilterProps = Pick<
  AllPaymentPlansForTableQueryVariables,
  | 'search'
  | 'status'
  | 'totalEntitledQuantityFrom'
  | 'totalEntitledQuantityTo'
  | 'dispersionStartDate'
  | 'dispersionEndDate'
  | 'isFollowUp'
>;

interface PaymentPlansFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const PaymentPlansFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: PaymentPlansFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();

  const {
    handleFilterChange,
    applyFilterChanges,
    clearFilter,
  } = createHandleApplyFilterChange(
    initialFilter,
    history,
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

  const { data: statusChoicesData } = usePaymentPlanStatusChoicesQueryQuery();

  if (!statusChoicesData) {
    return null;
  }

  return (
    <ContainerWithBorder>
      <Grid container spacing={3} alignItems='flex-end'>
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            fullWidth
            onChange={(e) => handleFilterChange('search', e.target.value)}
          />
        </Grid>
        <Grid item xs={3}>
          <FlexSelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            variant='outlined'
            label={t('Status')}
            multiple
            value={filter.status}
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
          </FlexSelectFilter>
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            id='totalEntitledQuantityFromFilter'
            topLabel={t('Entitled Quantity')}
            value={filter.totalEntitledQuantityFrom}
            placeholder={t('From')}
            onChange={(e) =>
              handleFilterChange('totalEntitledQuantityFrom', e.target.value)
            }
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            id='totalEntitledQuantityToFilter'
            value={filter.totalEntitledQuantityTo}
            placeholder={t('To')}
            onChange={(e) =>
              handleFilterChange('totalEntitledQuantityTo', e.target.value)
            }
            error={
              filter.totalEntitledQuantityFrom &&
              filter.totalEntitledQuantityTo &&
              filter.totalEntitledQuantityFrom > filter.totalEntitledQuantityTo
            }
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            topLabel={t('Dispersion Date')}
            placeholder={t('From')}
            onChange={(date) => {
              if (
                filter.dispersionEndDate &&
                date.isAfter(filter.dispersionEndDate)
              ) {
                handleFilterChange(
                  'dispersionStartDate',
                  date.format('YYYY-MM-DD'),
                );
                handleFilterChange('dispersionEndDate', undefined);
              } else {
                handleFilterChange(
                  'dispersionStartDate',
                  date.format('YYYY-MM-DD'),
                );
              }
            }}
            value={filter.dispersionStartDate}
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) =>
              handleFilterChange('dispersionEndDate', date.format('YYYY-MM-DD'))
            }
            value={filter.dispersionEndDate}
            minDate={filter.dispersionStartDate}
            minDateMessage={<span />}
          />
        </Grid>
        <Grid item xs={12}>
          <Box ml={2}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={Boolean(filter.isFollowUp)}
                  value={filter.isFollowUp}
                  color='primary'
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
      <ClearApplyButtons
        clearHandler={handleClearFilter}
        applyHandler={handleApplyFilter}
      />
    </ContainerWithBorder>
  );
};
