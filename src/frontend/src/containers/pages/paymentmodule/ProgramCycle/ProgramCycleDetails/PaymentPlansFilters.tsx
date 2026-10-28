import { FiltersSection } from '@components/core/FiltersSection';
import { allowedStatusChoices } from '@containers/tables/paymentmodule/PaymentPlansTable/PaymentPlansFilters';
import { DatePickerFilter } from '@core/DatePickerFilter';
import { NumberTextField } from '@core/NumberTextField';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { Title } from '@core/Title';
import { MenuItem, Typography } from '@mui/material';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';
import { Box } from '@mui/system';
import type { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { createHandleApplyFilterChange, formatFigure } from '@utils/utils';
import moment from 'moment';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';

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
}: PaymentPlansFilterProps): ReactElement => {
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

  const { data: statusChoicesData } = useQuery({
    queryKey: restQueryKey(RestService.restChoicesPaymentPlanStatusList),
    queryFn: () => RestService.restChoicesPaymentPlanStatusList(),
  });

  if (!statusChoicesData) {
    return null;
  }

  const preparedStatusChoices =
    [...(statusChoicesData || [])]?.filter((el) =>
      allowedStatusChoices.includes(el.value as PaymentPlanStatusEnum),
    ) || [];

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <Title>
        <Typography variant="h6">
          {t('Payment Plan Components Filters')}
        </Typography>
      </Title>
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
            {preparedStatusChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <NumberTextField
              id="totalEntitledQuantityFromFilter"
              topLabel={t('Total Entitled Quantity (USD)')}
              value={formatFigure(filter.totalEntitledQuantityFrom)}
              placeholder={t('From')}
              onChange={(e) =>
                handleFilterChange('totalEntitledQuantityFrom', e.target.value)
              }
            />
          </Box>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <NumberTextField
            id="totalEntitledQuantityToFilter"
            value={formatFigure(filter.totalEntitledQuantityTo)}
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
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
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </FiltersSection>
  );
};
