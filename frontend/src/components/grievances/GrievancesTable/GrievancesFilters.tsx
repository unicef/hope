import { Box, Grid, MenuItem, TextField } from '@material-ui/core';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useArrayToDict } from '../../../hooks/useArrayToDict';
import { RdiAutocomplete } from '../../../shared/RdiAutocomplete';
import { GRIEVANCE_CATEGORIES } from '../../../utils/constants';
import { GrievancesChoiceDataQuery } from '../../../__generated__/graphql';
import { ContainerWithBorder } from '../../core/ContainerWithBorder';
import { DatePickerFilter } from '../../core/DatePickerFilter';
import { FieldLabel } from '../../core/FieldLabel';
import { SearchTextField } from '../../core/SearchTextField';
import { SelectFilter } from '../../core/SelectFilter';
import { AdminAreaAutocomplete } from '../../population/AdminAreaAutocomplete';
import { AssigneeAutocomplete } from './AssigneeAutocomplete';

interface GrievancesFiltersProps {
  onFilterChange;
  filter;
  choicesData: GrievancesChoiceDataQuery;
}
export function GrievancesFilters({
  onFilterChange,
  filter,
  choicesData,
}: GrievancesFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });

  const issueTypeDict = useArrayToDict(
    choicesData?.grievanceTicketIssueTypeChoices,
    'category',
    '*',
  );
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            value={filter.search}
            label='Search'
            onChange={(e) => handleFilterChange(e, 'search')}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'status')}
            label={t('Status')}
            value={filter.status}
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
            value={filter.fsp}
            label='FSP'
            onChange={(e) => handleFilterChange(e, 'fsp')}
          />
        </Grid>
        <Grid item>
          <DatePickerFilter
            topLabel={t('Creation Date')}
            label='From'
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
            value={filter.createdAtRange.min}
          />
        </Grid>
        <Grid item>
          <DatePickerFilter
            label='To'
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
            value={filter.createdAtRange.max}
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'category')}
            label={t('Category')}
            value={filter.category}
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
          </SelectFilter>
        </Grid>
        {filter.category === GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE ||
        filter.category === GRIEVANCE_CATEGORIES.DATA_CHANGE ? (
          <Grid item>
            <SelectFilter
              onChange={(e) => handleFilterChange(e, 'issueType')}
              label='Issue Type'
              value={filter.issueType}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {issueTypeDict[filter.category].subCategories.map((item) => {
                return (
                  <MenuItem key={item.value} value={item.value}>
                    {item.name}
                  </MenuItem>
                );
              })}
            </SelectFilter>
          </Grid>
        ) : null}

        <Grid item>
          <AdminAreaAutocomplete onFilterChange={onFilterChange} name='admin' />
        </Grid>
        <Grid item>
          <AssigneeAutocomplete
            onFilterChange={onFilterChange}
            name='assignedTo'
          />
        </Grid>
        <Grid item>
          <Box display='flex' flexDirection='column'>
            <FieldLabel>{t('Similarity Score')}</FieldLabel>
            <TextField
              value={filter.scoreMin}
              variant='outlined'
              margin='dense'
              placeholder='From'
              onChange={(e) => handleFilterChange(e, 'scoreMin')}
              type='number'
            />
          </Box>
        </Grid>
        <Grid item>
          <Box display='flex' flexDirection='column'>
            <TextField
              value={filter.scoreMax}
              variant='outlined'
              margin='dense'
              placeholder='To'
              onChange={(e) => handleFilterChange(e, 'scoreMax')}
              type='number'
            />
          </Box>
        </Grid>
        <Grid item>
          <RdiAutocomplete
            onFilterChange={onFilterChange}
            name='registrationDataImport'
          />
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
