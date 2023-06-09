import { Grid, MenuItem } from '@material-ui/core';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import MonetizationOnIcon from '@material-ui/icons/MonetizationOn';
import moment from 'moment';
import React from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { ContainerWithBorder } from '../../../../components/core/ContainerWithBorder';
import { DatePickerFilter } from '../../../../components/core/DatePickerFilter';
import { SearchTextField } from '../../../../components/core/SearchTextField';
import { SelectFilter } from '../../../../components/core/SelectFilter';
import { createHandleFilterChange } from '../../../../utils/utils';
import {
  ProgramNode,
  useCashPlanVerificationStatusChoicesQuery,
} from '../../../../__generated__/graphql';

interface PaymentFiltersProps {
  onFilterChange;
  filter;
  programs: ProgramNode[];
}
export const PaymentFilters = ({
  onFilterChange,
  filter,
  programs,
}: PaymentFiltersProps): React.ReactElement => {
  const history = useHistory();
  const location = useLocation();
  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );

  const {
    data: statusChoicesData,
  } = useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) {
    return null;
  }

  return (
    <ContainerWithBorder>
      <Grid container spacing={3}>
        <Grid item xs={4}>
          <SearchTextField
            value={filter.search}
            data-cy='filter-search'
            label='Cash/Payment Plan ID'
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
        <Grid item xs={2}>
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
            label='Modality'
            data-cy='filter-Modality'
            value={filter.deliveryType}
            fullWidth
            icon={<MonetizationOnIcon />}
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
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
                moment(date)
                  .startOf('day')
                  .toISOString(),
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
              handleFilterChange(
                'endDate',
                moment(date)
                  .endOf('day')
                  .toISOString(),
              )
            }
            value={filter.endDate}
          />
        </Grid>
        <Grid item xs={6}>
          <SelectFilter
            onChange={(e) => handleFilterChange('program', e.target.value)}
            label='Programme'
            fullWidth
            data-cy='filter-program'
            value={filter.program}
            icon={<FlashOnIcon />}
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
            {programs.map((program) => (
              <MenuItem key={program.id} value={program.id}>
                {program.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
};
