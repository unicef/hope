import { Grid, MenuItem } from '@material-ui/core';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import MonetizationOnIcon from '@material-ui/icons/MonetizationOn';
import moment from 'moment';
import React from 'react';
import { ContainerWithBorder } from '../../../../components/core/ContainerWithBorder';
import { DatePickerFilter } from '../../../../components/core/DatePickerFilter';
import { SearchTextField } from '../../../../components/core/SearchTextField';
import { SelectFilter } from '../../../../components/core/SelectFilter';
import {
  ProgramNode,
  useCashPlanVerificationStatusChoicesQuery,
} from '../../../../__generated__/graphql';

interface PaymentFiltersProps {
  onFilterChange;
  filter;
  programs: ProgramNode[];
}
export function PaymentFilters({
  onFilterChange,
  filter,
  programs,
}: PaymentFiltersProps): React.ReactElement {
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
      <Grid container spacing={3}>
        <Grid item>
          <SearchTextField
            value={filter.search || ''}
            label='Cash/Payment Plan ID'
            onChange={(e) => handleFilterChange(e, 'search')}
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'verificationStatus')}
            label='Status'
            multiple
            value={filter.verificationStatus || []}
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
          <SearchTextField
            value={filter.serviceProvider || ''}
            label='FSP'
            onChange={(e) => handleFilterChange(e, 'serviceProvider')}
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'deliveryType')}
            label='Modality'
            value={filter.deliveryType || ''}
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
        <Grid item>
          <DatePickerFilter
            label='Start Date'
            onChange={(date) =>
              onFilterChange({
                ...filter,
                startDate: moment(date)
                  .startOf('day')
                  .toISOString(),
              })
            }
            value={filter.startDate}
          />
        </Grid>
        <Grid item>
          <DatePickerFilter
            label='End Date'
            onChange={(date) =>
              onFilterChange({
                ...filter,
                endDate: moment(date)
                  .endOf('day')
                  .toISOString(),
              })
            }
            value={filter.endDate}
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'program')}
            label='Programme'
            value={filter.program || ''}
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
}
