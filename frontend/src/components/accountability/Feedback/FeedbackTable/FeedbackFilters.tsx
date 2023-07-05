import { Grid, MenuItem } from '@material-ui/core';
import moment from 'moment';
import React from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useFeedbackIssueTypeChoicesQuery } from '../../../../__generated__/graphql';
import { ContainerWithBorder } from '../../../core/ContainerWithBorder';
import { DatePickerFilter } from '../../../core/DatePickerFilter';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { SearchTextField } from '../../../core/SearchTextField';
import { SelectFilter } from '../../../core/SelectFilter';
import { createHandleApplyFilterChange } from '../../../../utils/utils';
import { AssigneeAutocomplete } from '../../../../shared/autocompletes/AssigneeAutocomplete';
import { ClearApplyButtons } from '../../../core/ClearApplyButtons';

interface FeedbackFiltersProps {
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  filter;
}
export const FeedbackFilters = ({
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  filter,
}: FeedbackFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useFeedbackIssueTypeChoicesQuery();

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

  if (choicesLoading) return <LoadingComponent />;

  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            value={filter.feedbackId}
            label='Search'
            onChange={(e) => handleFilterChange('feedbackId', e.target.value)}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('issueType', e.target.value)}
            label={t('Issue Type')}
            value={filter.issueType}
            data-cy='filters-issue-type'
          >
            <MenuItem value=''>
              <em>{t('None')}</em>
            </MenuItem>
            {choicesData.feedbackIssueTypeChoices.map((issueType) => (
              <MenuItem key={issueType.name} value={issueType.value}>
                {issueType.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <AssigneeAutocomplete
            name='createdBy'
            filter={filter}
            value={filter.createdBy}
            label={t('Created by')}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy='filters-created-by'
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            topLabel={t('Creation Date')}
            label='From'
            onChange={(date) =>
              handleFilterChange(
                'createdAtRangeMin',
                moment(date)
                  .startOf('day')
                  .toISOString(),
              )
            }
            value={filter.createdAtRangeMin}
            data-cy='filters-creation-date-from'
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            label={t('To')}
            onChange={(date) =>
              handleFilterChange(
                'createdAtRangeMax',
                moment(date)
                  .endOf('day')
                  .toISOString(),
              )
            }
            value={filter.createdAtRangeMax}
            data-cy='filters-creation-date-to'
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
