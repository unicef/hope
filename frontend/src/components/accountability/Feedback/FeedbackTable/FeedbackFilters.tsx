import { Grid, MenuItem } from '@material-ui/core';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import {
  useAllProgramsForChoicesQuery,
  useFeedbackIssueTypeChoicesQuery,
} from '../../../../__generated__/graphql';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { CreatedByFeedbackAutocomplete } from '../../../../shared/autocompletes/CreatedByFeedbackAutocomplete';
import { createHandleApplyFilterChange } from '../../../../utils/utils';
import { DatePickerFilter } from '../../../core/DatePickerFilter';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { SearchTextField } from '../../../core/SearchTextField';
import { SelectFilter } from '../../../core/SelectFilter';
import { FiltersSection } from '../../../core/FiltersSection';

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
  const { businessArea, isAllPrograms } = useBaseUrl();
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useFeedbackIssueTypeChoicesQuery();
  const { data, loading } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });

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

  if (choicesLoading || loading) return <LoadingComponent />;

  const allPrograms = data?.allPrograms?.edges || [];
  const programs = allPrograms.map((edge) => edge.node);

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            value={filter.feedbackId}
            label='Search'
            onChange={(e) => handleFilterChange('feedbackId', e.target.value)}
            data-cy='filters-search'
          />
        </Grid>
        {isAllPrograms && (
          <Grid item xs={3}>
            <SelectFilter
              onChange={(e) => handleFilterChange('program', e.target.value)}
              label={t('Programme')}
              value={filter.program}
              icon={<FlashOnIcon />}
              fullWidth
              data-cy='filters-program'
            >
              <MenuItem value=''>
                <em>{t('None')}</em>
              </MenuItem>
              {programs.map((program) => (
                <MenuItem key={program.id} value={program.id}>
                  {program.name}
                </MenuItem>
              ))}
            </SelectFilter>
          </Grid>
        )}
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('issueType', e.target.value)}
            label={t('Issue Type')}
            value={filter.issueType}
            data-cy='filters-issue-type'
          >
            {choicesData?.feedbackIssueTypeChoices?.map((issueType) => (
              <MenuItem key={issueType.name} value={issueType.value}>
                {issueType.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <CreatedByFeedbackAutocomplete
            name='createdBy'
            filter={filter}
            value={filter.createdBy}
            label={t('Created by')}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            topLabel={t('Creation Date')}
            label='From'
            onChange={(date) => handleFilterChange('createdAtRangeMin', date)}
            value={filter.createdAtRangeMin}
            data-cy='filters-creation-date-from'
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            label={t('To')}
            onChange={(date) => handleFilterChange('createdAtRangeMax', date)}
            value={filter.createdAtRangeMax}
            data-cy='filters-creation-date-to'
          />
        </Grid>
        {isAllPrograms && (
          <Grid item xs={3}>
            <SelectFilter
              onChange={(e) =>
                handleFilterChange('programState', e.target.value)
              }
              label={t('Programme State')}
              value={filter.programState}
              fullWidth
              disableClearable
              data-cy='filters-program-state'
            >
              <MenuItem value='active'>{t('Active Programmes')}</MenuItem>
              <MenuItem value='all'>{t('All Programmes')}</MenuItem>
            </SelectFilter>
          </Grid>
        )}
      </Grid>
    </FiltersSection>
  );
};
