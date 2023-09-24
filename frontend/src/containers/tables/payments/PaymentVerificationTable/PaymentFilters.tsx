import { Grid, MenuItem } from '@material-ui/core';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import MonetizationOnIcon from '@material-ui/icons/MonetizationOn';
import React from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import {
  ProgramNode,
  useCashPlanVerificationStatusChoicesQuery,
} from '../../../../__generated__/graphql';
import { ClearApplyButtons } from '../../../../components/core/ClearApplyButtons';
import { ContainerWithBorder } from '../../../../components/core/ContainerWithBorder';
import { DatePickerFilter } from '../../../../components/core/DatePickerFilter';
import { SearchTextField } from '../../../../components/core/SearchTextField';
import { SelectFilter } from '../../../../components/core/SelectFilter';
import {
  createHandleApplyFilterChange,
  dateToIsoString,
} from '../../../../utils/utils';

interface PaymentFiltersProps {
  filter;
  programs: ProgramNode[];
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const PaymentFilters = ({
  filter,
  programs,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: PaymentFiltersProps): React.ReactElement => {
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

  const {
    data: statusChoicesData,
  } = useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) {
    return null;
  }

  return (
    <ContainerWithBorder>
      <Grid container spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            value={filter.search}
            data-cy='filter-search'
            label='Payment Plan ID'
            onChange={(e) => handleFilterChange('search', e.target.value)}
            fullWidth
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('verificationStatus', e.target.value)
            }
            label='Status'
            multiple
            fullWidth
            data-cy='filter-status'
            value={filter.verificationStatus}
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
        <Grid item xs={3}>
          <SearchTextField
            value={filter.serviceProvider}
            data-cy='filter-fsp'
            label='FSP'
            fullWidth
            onChange={(e) =>
              handleFilterChange('serviceProvider', e.target.value)
            }
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('deliveryType', e.target.value)}
            label='Delivery Mechanism'
            data-cy='filter-Modality'
            value={filter.deliveryType}
            fullWidth
            icon={<MonetizationOnIcon />}
          >
            {statusChoicesData.paymentRecordDeliveryTypeChoices.map((item) => (
              <MenuItem key={item.name} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            label='Start Date'
            fullWidth
            data-cy='filter-start-date'
            onChange={(date) =>
              handleFilterChange(
                'startDate',
                dateToIsoString(date, 'startOfDay'),
              )
            }
            value={filter.startDate}
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            label='End Date'
            fullWidth
            data-cy='filter-end-date'
            onChange={(date) =>
              handleFilterChange('endDate', dateToIsoString(date, 'endOfDay'))
            }
            value={filter.endDate}
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('program', e.target.value)}
            label='Programme'
            fullWidth
            data-cy='filter-program'
            value={filter.program}
            icon={<FlashOnIcon />}
          >
            {programs.map((program) => (
              <MenuItem key={program.id} value={program.id}>
                {program.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
      </Grid>
      <ClearApplyButtons
        clearHandler={handleClearFilter}
        applyHandler={handleApplyFilter}
      />
    </ContainerWithBorder>
  );
};
