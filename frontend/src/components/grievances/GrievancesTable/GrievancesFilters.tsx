import { Box, Grid, MenuItem } from '@material-ui/core';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { GrievancesChoiceDataQuery } from '../../../__generated__/graphql';
import { useArrayToDict } from '../../../hooks/useArrayToDict';
import { AssigneeAutocomplete } from '../../../shared/AssigneeAutocomplete/AssigneeAutocomplete';
import { LanguageAutocomplete } from '../../../shared/LanguageAutocomplete';
import { RdiAutocomplete } from '../../../shared/RdiAutocomplete';
import { GRIEVANCE_CATEGORIES } from '../../../utils/constants';
import { createHandleApplyFilterChange } from '../../../utils/utils';
import { ClearApplyButtons } from '../../core/ClearApplyButtons';
import { ContainerWithBorder } from '../../core/ContainerWithBorder';
import { DatePickerFilter } from '../../core/DatePickerFilter';
import { NumberTextField } from '../../core/NumberTextField';
import { SearchTextField } from '../../core/SearchTextField';
import { SelectFilter } from '../../core/SelectFilter';
import { AdminAreaAutocomplete } from '../../population/AdminAreaAutocomplete';

interface GrievancesFiltersProps {
  filter;
  choicesData: GrievancesChoiceDataQuery;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const GrievancesFilters = ({
  filter,
  choicesData,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: GrievancesFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();

  const {
    handleFilterChange,
    applyFilterChanges,
    clearFilter,
  } = createHandleApplyFilterChange(
    initialFilter,
    history,
    location,
    filter,
    setFilter,
    appliedFilter,
    setAppliedFilter,
  );

  const handleApplyFilter = (): void => {
    applyFilterChanges();
  };

  const handleClearFilter = (): void => {
    clearFilter();
  };

  const issueTypeDict = useArrayToDict(
    choicesData?.grievanceTicketIssueTypeChoices,
    'category',
    '*',
  );
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            value={filter.search}
            label='Search'
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
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
        <Grid item xs={3}>
          <SearchTextField
            value={filter.fsp}
            label='FSP'
            onChange={(e) => handleFilterChange('fsp', e.target.value)}
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            topLabel={t('Creation Date')}
            placeholder='From'
            onChange={(date) =>
              handleFilterChange(
                'createdAtRangeMin',
                moment(date)
                  .set({ hour: 0, minute: 0 })
                  .toISOString(),
              )
            }
            value={filter.createdAtRangeMin}
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            placeholder='To'
            onChange={(date) =>
              handleFilterChange(
                'createdAtRangeMax',
                moment(date)
                  .set({ hour: 23, minute: 59 })
                  .toISOString(),
              )
            }
            value={filter.createdAtRangeMax}
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('category', e.target.value)}
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
          <Grid item xs={3}>
            <SelectFilter
              onChange={(e) => handleFilterChange('issueType', e.target.value)}
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

        <Grid item xs={3}>
          <AdminAreaAutocomplete
            filter={filter}
            name='admin'
            value={filter.admin}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </Grid>
        <Grid item xs={3}>
          <AssigneeAutocomplete
            filter={filter}
            name='userId'
            value={filter.userId}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            topLabel={t('Similarity Score')}
            value={filter.scoreMin}
            placeholder={t('From')}
            onChange={(e) => handleFilterChange('scoreMin', e.target.value)}
          />
        </Grid>
        <Grid item xs={3}>
          <Box display='flex' flexDirection='column'>
            <NumberTextField
              value={filter.scoreMax}
              placeholder='To'
              onChange={(e) => handleFilterChange('scoreMax', e.target.value)}
            />
          </Box>
        </Grid>
        <Grid item xs={3}>
          <RdiAutocomplete
            filter={filter}
            name='registrationDataImport'
            value={filter.registrationDataImport}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            setFilter={setFilter}
          />
        </Grid>
        <Grid item xs={3}>
          <LanguageAutocomplete
            filter={filter}
            name='preferredLanguage'
            value={filter.preferredLanguage}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            setFilter={setFilter}
          />
        </Grid>
      </Grid>
      <ClearApplyButtons
        clearHandler={handleClearFilter}
        applyHandler={handleApplyFilter}
      />
    </ContainerWithBorder>
  );
};
