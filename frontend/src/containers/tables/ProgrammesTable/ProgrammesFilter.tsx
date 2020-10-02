import {
  FormControl,
  Grid,
  InputAdornment,
  MenuItem,
  TextField,
} from '@material-ui/core';
import GroupIcon from '@material-ui/icons/Group';
import moment from 'moment';
import React from 'react';
import styled from 'styled-components';
import SearchIcon from '@material-ui/icons/Search';
import { ProgrammeChoiceDataQuery } from '../../../__generated__/graphql';
import InputLabel from '../../../shared/InputLabel';
import Select from '../../../shared/Select';
import { KeyboardDatePicker } from '@material-ui/pickers';

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

interface ProgrammesFilterProps {
  onFilterChange;
  filter;
  choicesData: ProgrammeChoiceDataQuery;
}
export function ProgrammesFilters({
  onFilterChange,
  filter,
  choicesData,
}: ProgrammesFilterProps): React.ReactElement {
  console.log(choicesData);
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <Container>
      <Grid container>
        <Grid item xs={2}>
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
            data-cy='filters-search'
          />
        </Grid>
        <Grid item xs={2}>
          <KeyboardDatePicker
            variant='inline'
            disableToolbar
            inputVariant='outlined'
            margin='dense'
            label='Start Date'
            autoOk
            onChange={(date) =>
              onFilterChange({
                ...filter,
                startDate: moment(date).toISOString(),
              })
            }
            value={filter.startDate || null}
            format='D MMM YYYY'
            InputAdornmentProps={{ position: 'end' }}
          />
        </Grid>
        <Grid item xs={2}>
          <KeyboardDatePicker
            variant='inline'
            disableToolbar
            inputVariant='outlined'
            margin='dense'
            label='End Date'
            autoOk
            onChange={(date) =>
              onFilterChange({ ...filter, endDate: moment(date).toISOString() })
            }
            value={filter.endDate || null}
            format='D MMM YYYY'
            InputAdornmentProps={{ position: 'end' }}
          />
        </Grid>
        <Grid item xs={2}>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Status</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'status')}
              variant='outlined'
              label='Status'
              value={[...filter.status] || []}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {choicesData.programStatusChoices.map((item) => {
                return (
                  <MenuItem key={item.value} value={item.value}>
                    {item.name}
                  </MenuItem>
                );
              })}
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item xs={2}>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Sector</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'sector')}
              variant='outlined'
              label='Sector'
              value={[...filter.sector] || []}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {choicesData.programSectorChoices.map((item) => {
                return (
                  <MenuItem key={item.value} value={item.value}>
                    {item.name}
                  </MenuItem>
                );
              })}
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item xs={2}>
          <TextContainer
            value={filter.householdSize.min}
            variant='outlined'
            margin='dense'
            label='Household size'
            onChange={(e) =>
              onFilterChange({
                ...filter,
                householdSize: {
                  ...filter.householdSize,
                  min: e.target.value || undefined,
                },
              })
            }
            type='number'
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <GroupIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item xs={2}>
          to
          <TextContainer
            value={filter.householdSize.max}
            variant='outlined'
            margin='dense'
            label='Household size'
            onChange={(e) =>
              onFilterChange({
                ...filter,
                householdSize: {
                  ...filter.householdSize,
                  max: e.target.value || undefined,
                },
              })
            }
            type='number'
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <GroupIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item xs={2}>
          <TextContainer
            value={filter.budget.min}
            variant='outlined'
            margin='dense'
            label='Budget'
            onChange={(e) =>
              onFilterChange({
                ...filter,
                budget: {
                  ...filter.budget,
                  min: e.target.value || undefined,
                },
              })
            }
            type='number'
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <GroupIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item xs={2}>
          to
          <TextContainer
            id='maxFilter'
            value={filter.budget.max}
            variant='outlined'
            margin='dense'
            label='Budget'
            onChange={(e) =>
              onFilterChange({
                ...filter,
                budget: {
                  ...filter.budget,
                  max: e.target.value || undefined,
                },
              })
            }
            type='number'
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <GroupIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
      </Grid>
    </Container>
  );
}
