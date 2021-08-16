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
import AccountBalanceIcon from '@material-ui/icons/AccountBalance';
import SearchIcon from '@material-ui/icons/Search';
import { KeyboardDatePicker } from '@material-ui/pickers';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { GrievancesChoiceDataQuery } from '../../../__generated__/graphql';
import { ContainerWithBorder } from '../../ContainerWithBorder';
import { FieldLabel } from '../../FieldLabel';
import { AdminAreasAutocomplete } from '../../population/AdminAreaAutocomplete';

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
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
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
            <InputLabel>{t('Status')}</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'status')}
              variant='outlined'
              label={t('Status')}
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
            label={t('FSP')}
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
                      .startOf('day')
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
            label={t('To')}
            autoOk
            onChange={(date) =>
              onFilterChange({
                ...filter,
                createdAtRange: {
                  ...filter.createdAtRange,
                  max: moment(date)
                    .endOf('day')
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
            {t('Clear')}
          </Button>
          <Button
            color='primary'
            variant='outlined'
            onClick={() => setFilterApplied(filter)}
          >
            {t('Apply')}
          </Button>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
