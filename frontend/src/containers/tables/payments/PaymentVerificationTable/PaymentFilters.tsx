import { Grid, InputAdornment, MenuItem } from '@material-ui/core';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import MonetizationOnIcon from '@material-ui/icons/MonetizationOn';
import { KeyboardDatePicker } from '@material-ui/pickers';
import moment from 'moment';
import React from 'react';
import styled from 'styled-components';
import { ContainerWithBorder } from '../../../../components/core/ContainerWithBorder';
import { SearchTextField } from '../../../../components/core/SearchTextField';
import { StyledFormControl } from '../../../../components/StyledFormControl';
import InputLabel from '../../../../shared/InputLabel';
import Select from '../../../../shared/Select';
import {
  ProgramNode,
  useCashPlanVerificationStatusChoicesQuery,
} from '../../../../__generated__/graphql';

const StartInputAdornment = styled(InputAdornment)`
  margin-right: 0;
`;

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
            label='Cash Plan ID'
            onChange={(e) => handleFilterChange(e, 'search')}
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Status</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'verificationStatus')}
              variant='outlined'
              label='Status'
              multiple
              value={filter.verificationStatus || []}
            >
              {statusChoicesData.cashPlanVerificationStatusChoices.map(
                (item) => {
                  return (
                    <MenuItem key={item.value} value={item.value}>
                      {item.name}
                    </MenuItem>
                  );
                },
              )}
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item>
          <SearchTextField
            value={filter.serviceProvider || ''}
            label='FSP'
            onChange={(e) => handleFilterChange(e, 'serviceProvider')}
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Modality</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'deliveryType')}
              variant='outlined'
              label='Modality'
              value={filter.deliveryType || ''}
              InputProps={{
                startAdornment: (
                  <StartInputAdornment position='start'>
                    <MonetizationOnIcon />
                  </StartInputAdornment>
                ),
              }}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {statusChoicesData.paymentRecordDeliveryTypeChoices.map(
                (item) => (
                  <MenuItem key={item.name} value={item.value}>
                    {item.name}
                  </MenuItem>
                ),
              )}
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item>
          <KeyboardDatePicker
            variant='inline'
            inputVariant='outlined'
            margin='dense'
            label='Start Date'
            autoOk
            onChange={(date) =>
              onFilterChange({
                ...filter,
                startDate: moment(date)
                  .startOf('day')
                  .toISOString(),
              })
            }
            value={filter.startDate || null}
            format='YYYY-MM-DD'
            InputAdornmentProps={{ position: 'end' }}
          />
        </Grid>
        <Grid item>
          <KeyboardDatePicker
            variant='inline'
            inputVariant='outlined'
            margin='dense'
            label='End Date'
            autoOk
            onChange={(date) =>
              onFilterChange({
                ...filter,
                endDate: moment(date)
                  .endOf('day')
                  .toISOString(),
              })
            }
            value={filter.endDate || null}
            format='YYYY-MM-DD'
            InputAdornmentProps={{ position: 'end' }}
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Programme</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'program')}
              variant='outlined'
              label='Programme'
              value={filter.program || ''}
              InputProps={{
                startAdornment: (
                  <StartInputAdornment position='start'>
                    <FlashOnIcon />
                  </StartInputAdornment>
                ),
              }}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {programs.map((program) => (
                <MenuItem key={program.id} value={program.id}>
                  {program.name}
                </MenuItem>
              ))}
            </Select>
          </StyledFormControl>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
