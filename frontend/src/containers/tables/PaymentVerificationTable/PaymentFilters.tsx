import React from 'react';
import styled from 'styled-components';
import { InputAdornment, MenuItem, Grid } from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import AccountBalanceIcon from '@material-ui/icons/AccountBalance';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import FormControl from '@material-ui/core/FormControl';
import MonetizationOnIcon from '@material-ui/icons/MonetizationOn';
import TextField from '../../../shared/TextField';
import InputLabel from '../../../shared/InputLabel';
import Select from '../../../shared/Select';
import { KeyboardDatePicker } from '@material-ui/pickers';
import {
  ProgramNode,
  useCashPlanVerificationStatusChoicesQuery,
} from '../../../__generated__/graphql';

// import { AdminAreasAutocomplete } from './AdminAreaAutocomplete';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: row;
  align-items: center;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;

  && > div {
    margin: 5px;
  }
`;

const TextContainer = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
`;
const StyledFormControl = styled(FormControl)`
  width: 232px;
  color: #5f6368;
  border-bottom: 0;
`;

const SearchTextField = styled(TextField)`
  flex: 1;
  && {
    min-width: 150px;
  }
`;

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
    <Container>
      <Grid container spacing={3}>
        <Grid item>
          <SearchTextField
            label='Search'
            variant='outlined'
            margin='dense'
            onChange={(e) => handleFilterChange(e, 'search')}
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
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
        <Grid item>
          <SearchTextField
            label='FSP'
            variant='outlined'
            margin='dense'
            onChange={(e) => handleFilterChange(e, 'assistanceThrough')}
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <AccountBalanceIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item>
          {/* NEED TO ADD FILTERS ON THE BACKEND */}
          <KeyboardDatePicker
            variant='inline'
            disableToolbar
            inputVariant='outlined'
            margin='dense'
            label='Start Date'
            autoOk
            onChange={(date) => onFilterChange({ ...filter, startDate: date })}
            value={filter.startDate || null}
            format='DD/MM/YYYY'
            InputAdornmentProps={{ position: 'end' }}
          />
        </Grid>
        <Grid item>
          <KeyboardDatePicker
            variant='inline'
            disableToolbar
            inputVariant='outlined'
            margin='dense'
            label='End Date'
            autoOk
            onChange={(date) => onFilterChange({ ...filter, endDate: date })}
            value={filter.endDate || null}
            format='DD/MM/YYYY'
            InputAdornmentProps={{ position: 'end' }}
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
              {[
                { name: 'Deposit to Card', id: 1 },
                { name: 'Cash', id: 2 },
                { name: 'Transfer', id: 3 },
              ].map((item) => (
                <MenuItem key={item.name} value={item.name}>
                  {item.name}
                </MenuItem>
              ))}
            </Select>
          </StyledFormControl>
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
              value={filter.verificationStatus || ''}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
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
      </Grid>
    </Container>
  );
}
