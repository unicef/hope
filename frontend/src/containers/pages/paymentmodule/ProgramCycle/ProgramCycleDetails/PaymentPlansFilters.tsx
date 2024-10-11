import React from 'react';
import {
  AllPaymentPlansForTableQueryVariables,
  usePaymentPlanStatusChoicesQueryQuery,
} from '@generated/graphql';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { createHandleApplyFilterChange } from '@utils/utils';
import { ContainerWithBorder } from '@core/ContainerWithBorder';
import { Title } from '@core/Title';
import { MenuItem, Typography } from '@mui/material';
import Grid from '@mui/material/Grid';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { NumberTextField } from '@core/NumberTextField';
import { Box } from '@mui/system';
import { DatePickerFilter } from '@core/DatePickerFilter';
import moment from 'moment';
import { ClearApplyButtons } from '@core/ClearApplyButtons';

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

const FilterSectionWrapper = styled.div`
  padding: 20 20 0 20;
`;

interface PaymentPlansFilterProps {
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
}: PaymentPlansFilterProps): React.ReactElement => {
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

  const { data: statusChoicesData } = usePaymentPlanStatusChoicesQueryQuery();

  if (!statusChoicesData) {
    return null;
  }

  return (
    <FilterSectionWrapper>
      <ContainerWithBorder>
        <Title>
          <Typography variant="h6">{t('Payment Plans Filters')}</Typography>
        </Title>
        <Grid container spacing={3} alignItems="flex-end">
          <Grid item xs={3}>
            <SearchTextField
              label={t('Search')}
              value={filter.search}
              fullWidth
              onChange={(e) => handleFilterChange('search', e.target.value)}
            />
          </Grid>
          <Grid item xs={3}>
            <SelectFilter
              onChange={(e) => handleFilterChange('status', e.target.value)}
              variant="outlined"
              label={t('Status')}
              multiple
              value={filter.status}
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
          <Grid item xs={3}>
            <Box display="flex" flexDirection="column">
              <NumberTextField
                id="totalEntitledQuantityFromFilter"
                topLabel={t('Total Entitled Quantity (USD)')}
                value={filter.totalEntitledQuantityFrom}
                placeholder={t('From')}
                onChange={(e) =>
                  handleFilterChange(
                    'totalEntitledQuantityFrom',
                    e.target.value,
                  )
                }
              />
            </Box>
          </Grid>
          <Grid item xs={3}>
            <NumberTextField
              id="totalEntitledQuantityToFilter"
              value={filter.totalEntitledQuantityTo}
              placeholder={t('To')}
              onChange={(e) =>
                handleFilterChange('totalEntitledQuantityTo', e.target.value)
              }
              error={
                filter.totalEntitledQuantityFrom &&
                filter.totalEntitledQuantityTo &&
                filter.totalEntitledQuantityFrom >
                  filter.totalEntitledQuantityTo
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
                  moment(date).isAfter(filter.dispersionEndDate)
                ) {
                  handleFilterChange(
                    'dispersionStartDate',
                    moment(date).format('YYYY-MM-DD'),
                  );
                  handleFilterChange('dispersionEndDate', undefined);
                } else {
                  handleFilterChange(
                    'dispersionStartDate',
                    moment(date).format('YYYY-MM-DD'),
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
                handleFilterChange(
                  'dispersionEndDate',
                  moment(date).format('YYYY-MM-DD'),
                )
              }
              value={filter.dispersionEndDate}
              minDate={filter.dispersionStartDate}
              minDateMessage={<span />}
            />
          </Grid>
        </Grid>
        <ClearApplyButtons
          clearHandler={handleClearFilter}
          applyHandler={handleApplyFilter}
        />
      </ContainerWithBorder>
    </FilterSectionWrapper>
  );
};
