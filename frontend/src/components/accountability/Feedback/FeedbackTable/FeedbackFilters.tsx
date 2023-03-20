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
import { createHandleFilterChange } from '../../../../utils/utils';
import { AssigneeAutocomplete } from '../../../../shared/autocompletes/AssigneeAutocomplete';

interface FeedbackFiltersProps {
  onFilterChange;
  filter;
}
export const FeedbackFilters = ({
  onFilterChange,
  filter,
}: FeedbackFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useFeedbackIssueTypeChoicesQuery();

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );

  if (choicesLoading) return <LoadingComponent />;

  return (
    <ContainerWithBorder>
      <Grid container alignItems='center' spacing={3}>
        <Grid item xs={4}>
          <SearchTextField
            value={filter.feedbackId}
            label='Search'
            onChange={(e) => handleFilterChange('feedbackId', e.target.value)}
            data-cy='filters-search'
            fullWidth
          />
        </Grid>
        <Grid item xs={4}>
          <SelectFilter
            onChange={(e) => handleFilterChange('issueType', e.target.value)}
            label={t('Issue Type')}
            value={filter.issueType}
            fullWidth
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
        <Grid item xs={4}>
          <AssigneeAutocomplete
            onFilterChange={onFilterChange}
            name='createdBy'
            filter={filter}
            value={filter.createdBy}
            label={t('Created by')}
            fullWidth
          />
        </Grid>
        <Grid container item xs={6} spacing={3} alignItems='flex-end'>
          <Grid item xs={6}>
            <DatePickerFilter
              topLabel={t('Creation Date')}
              label='From'
              onChange={(date) =>
                handleFilterChange(
                  'createdAtRange',
                  moment(date)
                    .startOf('day')
                    .toISOString(),
                )
              }
              value={filter.createdAtRangeMin}
            />
          </Grid>
          <Grid item xs={6}>
            <DatePickerFilter
              label={t('To')}
              onChange={(date) =>
                handleFilterChange(
                  'createdAtRange',
                  moment(date)
                    .endOf('day')
                    .toISOString(),
                )
              }
              value={filter.createdAtRangeMax}
            />
          </Grid>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
};
