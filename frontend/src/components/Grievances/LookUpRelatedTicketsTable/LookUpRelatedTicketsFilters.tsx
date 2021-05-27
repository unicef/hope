import React from 'react';
import styled from 'styled-components';
import moment from 'moment';
import {
  Box,
  Button,
  FormControl,
  Grid,
  InputAdornment,
  InputLabel,
  MenuItem,
  Select,
  TextField,
} from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import AccountBalanceIcon from '@material-ui/icons/AccountBalance';
import {KeyboardDatePicker} from '@material-ui/pickers';
import {ContainerWithBorder} from '../../ContainerWithBorder';
import {AdminAreasAutocomplete} from '../../population/AdminAreaAutocomplete';
import {FieldLabel} from '../../FieldLabel';
import {GrievancesChoiceDataQuery} from '../../../__generated__/graphql';

const SearchTextField = styled(TextField)`
  flex: 1;
  && {
    min-width: 150px;
  }
`;
const StyledFormControl = styled(FormControl)`
  width: 232px;
  color: #5f6368;
  border-bottom: 0;
`;

interface LookUpRelatedTicketsFiltersProps {
  onFilterChange;
  filter;
  choicesData: GrievancesChoiceDataQuery;
  setFilterApplied?;
  filterInitial?;
}
export function LookUpRelatedTicketsFilters({
  onFilterChange,
  filter,
  choicesData,
  setFilterApplied,
  filterInitial,
}: LookUpRelatedTicketsFiltersProps): React.ReactElement {
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label='Search'
            variant='outlined'
            margin='dense'
            value={filter.search}
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
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Status</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'status')}
              variant='outlined'
              label='Status'
              value={filter.status || null}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {choicesData.grievanceTicketStatusChoices.map((item) => {
                return (
                  <MenuItem key={item.value} value={item.value}>
                    {item.name}
                  </MenuItem>
                );
              })}
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item>
          <SearchTextField
            label='FSP'
            variant='outlined'
            margin='dense'
            value={filter.fsp}
            onChange={(e) => handleFilterChange(e, 'fsp')}
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
          <Box display='flex' flexDirection='column'>
            <FieldLabel>Creation Date</FieldLabel>
            <KeyboardDatePicker
              variant='inline'
              disableToolbar
              inputVariant='outlined'
              margin='dense'
              label='From'
              autoOk
              onChange={(date) =>
                onFilterChange({
                  ...filter,
                  createdAtRange: {
                    ...filter.createdAtRange,
                    min: moment(date).startOf('day').toISOString(),
                  },
                })
              }
              value={filter.createdAtRange.min || null}
              format='YYYY-MM-DD'
              InputAdornmentProps={{ position: 'end' }}
            />
          </Box>
        </Grid>
        <Grid item>
          <KeyboardDatePicker
            variant='inline'
            disableToolbar
            inputVariant='outlined'
            margin='dense'
            label='To'
            autoOk
            onChange={(date) =>
              onFilterChange({
                ...filter,
                createdAtRange: {
                  ...filter.createdAtRange,
                  max: moment(date).endOf('day').toISOString(),
                },
              })
            }
            value={filter.createdAtRange.max || null}
            format='YYYY-MM-DD'
            InputAdornmentProps={{ position: 'end' }}
          />
        </Grid>
        <Grid item>
          <AdminAreasAutocomplete
            onFilterChange={onFilterChange}
            name='admin'
          />
        </Grid>
        <Grid container justify='flex-end'>
          <Button
            color='primary'
            onClick={() => {
              setFilterApplied(filterInitial);
              onFilterChange(filterInitial);
            }}
          >
            Clear
          </Button>
          <Button
            color='primary'
            variant='outlined'
            onClick={() => setFilterApplied(filter)}
          >
            Apply
          </Button>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
