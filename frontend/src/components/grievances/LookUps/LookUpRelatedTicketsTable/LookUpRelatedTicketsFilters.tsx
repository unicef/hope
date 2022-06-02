import { Box, Button, Grid, MenuItem } from '@material-ui/core';
import { KeyboardDatePicker } from '@material-ui/pickers';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { GrievancesChoiceDataQuery } from '../../../../__generated__/graphql';
import { ContainerWithBorder } from '../../../core/ContainerWithBorder';
import { FieldLabel } from '../../../core/FieldLabel';
import { SearchTextField } from '../../../core/SearchTextField';
import { SelectFilter } from '../../../core/SelectFilter';
import { AdminAreaAutocomplete } from '../../../population/AdminAreaAutocomplete';

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
            value={filter.search}
            onChange={(e) => handleFilterChange(e, 'search')}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'status')}
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
          </SelectFilter>
        </Grid>
        <Grid item>
          <SearchTextField
            label={t('FSP')}
            value={filter.fsp}
            onChange={(e) => handleFilterChange(e, 'fsp')}
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
          <AdminAreaAutocomplete onFilterChange={onFilterChange} name='admin' />
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
