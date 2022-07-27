import { Box, Grid, MenuItem, TextField } from '@material-ui/core';
import moment from 'moment';
import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { AccountBalance } from '@material-ui/icons';
import { useArrayToDict } from '../../../hooks/useArrayToDict';
import { RdiAutocomplete } from '../../../shared/RdiAutocomplete';
import {
  GrievanceSearchTypes,
  GrievanceStatuses,
  GrievanceTypes,
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_TICKETS_TYPES,
  GRIEVANCE_TICKET_STATES,
} from '../../../utils/constants';
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
  const handleFilterChange = (e, name): void => {
    onFilterChange({
      ...filter,
      [name]: e.target.value,
      ...(name === 'status' &&
        +e.target.value === GRIEVANCE_TICKET_STATES.CLOSED && {
          grievanceStatus: GrievanceStatuses.All,
        }),
    });
  };

  const issueTypeDict = useArrayToDict(
    choicesData?.grievanceTicketIssueTypeChoices,
    'category',
    '*',
  );

  const categoryChoices = useMemo(() => {
    return filter.grievanceType ===
      GrievanceTypes[GRIEVANCE_TICKETS_TYPES.userGenerated]
      ? choicesData.grievanceTicketManualCategoryChoices
      : choicesData.grievanceTicketSystemCategoryChoices;
  }, [choicesData, filter.grievanceType]);

  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            value={filter.search || ''}
            label='Search'
            onChange={(e) => handleFilterChange(e, 'search')}
            data-cy='filters-search'
          />
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'searchType')}
            label={undefined}
            value={filter.searchType || ''}
          >
            {Object.keys(GrievanceSearchTypes).map((key) => (
              <MenuItem
                key={GrievanceSearchTypes[key]}
                value={GrievanceSearchTypes[key]}
              >
                {key.replace(/\B([A-Z])\B/g, ' $1')}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'status')}
            label={t('Status')}
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
          </SelectFilter>
        </Grid>
        <Grid item>
          <SearchTextField
            value={filter.fsp || ''}
            label='FSP'
            icon={<AccountBalance style={{ color: '#5f6368' }} />}
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
            value={filter.category || ''}
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
            {categoryChoices.map((item) => {
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
              value={filter.issueType || ''}
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
              value={filter.scoreMin || null}
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
              value={filter.scoreMax || null}
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
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'priority')}
            label={t('Priority')}
            value={filter.priority || ''}
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
            {choicesData.grievanceTicketPriorityChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'urgency')}
            label={t('Urgency')}
            value={filter.urgency || ''}
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
            {choicesData.grievanceTicketUrgencyChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'grievanceStatus')}
            label={undefined}
            value={filter.grievanceStatus || ''}
          >
            <MenuItem value={GrievanceStatuses.Active}>
              {t('Active Tickets')}
            </MenuItem>
            <MenuItem value={GrievanceStatuses.All}>
              {t('All Tickets')}
            </MenuItem>
          </SelectFilter>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
