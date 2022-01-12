import {
  Box,
  FormControl,
  Grid,
  InputAdornment,
  InputLabel,
  MenuItem,
  Select,
} from '@material-ui/core';
import AccountBalanceIcon from '@material-ui/icons/AccountBalance';
import SearchIcon from '@material-ui/icons/Search';
import { KeyboardDatePicker } from '@material-ui/pickers';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import TextField from '../../../shared/TextField';
import { GrievancesChoiceDataQuery } from '../../../__generated__/graphql';
import { ContainerWithBorder } from '../../ContainerWithBorder';
import { FieldLabel } from '../../FieldLabel';
import { AdminAreaAutocomplete } from '../../Population/AdminAreaAutocomplete';

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

interface GrievancesFiltersProps {
  onFilterChange;
  filter;
  choicesData: GrievancesChoiceDataQuery;
  usersChoices;
}
export function GrievancesFilters({
  onFilterChange,
  filter,
  choicesData,
  usersChoices,
}: GrievancesFiltersProps): React.ReactElement {
  const { t } = useTranslation();
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
            onChange={(e) => handleFilterChange(e, 'search')}
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            data-cy='filters-search'
            value={filter.search || ''}
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>{t('Status')}</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'status')}
              variant='outlined'
              label='Status'
              value={filter.status || ''}
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
            <FieldLabel>{t('Creation Date')}</FieldLabel>
            <KeyboardDatePicker
              variant='inline'
              inputVariant='outlined'
              margin='dense'
              label='From'
              autoOk
              onChange={(date) =>
                onFilterChange({
                  ...filter,
                  createdAtRange: {
                    ...filter.createdAtRange,
                    min: moment(date)
                      .set({ hour: 0, minute: 0 })
                      .toISOString(),
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
            inputVariant='outlined'
            margin='dense'
            label='To'
            autoOk
            onChange={(date) =>
              onFilterChange({
                ...filter,
                createdAtRange: {
                  ...filter.createdAtRange,
                  max: moment(date)
                    .set({ hour: 23, minute: 59 })
                    .toISOString(),
                },
              })
            }
            value={filter.createdAtRange.max || null}
            format='YYYY-MM-DD'
            InputAdornmentProps={{ position: 'end' }}
          />
        </Grid>
        <Grid item>
          <AdminAreaAutocomplete onFilterChange={onFilterChange} name='admin' />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Category</InputLabel>
            <Select
              onChange={(e) => handleFilterChange(e, 'category')}
              variant='outlined'
              label='Category'
              value={filter.category || ''}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {choicesData.grievanceTicketCategoryChoices.map((item) => {
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
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>{t('Assignee')}</InputLabel>
            <Select
              onChange={(e) => handleFilterChange(e, 'assignedTo')}
              variant='outlined'
              label={t('Assignee')}
              value={filter.assignedTo || ''}
            >
              <MenuItem value=''>
                <em>{t('None')}</em>
              </MenuItem>
              {usersChoices.map((item) => {
                return (
                  <MenuItem key={item.value} value={item.value}>
                    {item.name}
                  </MenuItem>
                );
              })}
            </Select>
          </StyledFormControl>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
