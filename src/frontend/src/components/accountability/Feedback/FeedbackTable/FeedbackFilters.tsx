import withErrorBoundary from '@components/core/withErrorBoundary';
import { DatePickerFilter } from '@core/DatePickerFilter';
import { FiltersSection } from '@core/FiltersSection';
import { LoadingComponent } from '@core/LoadingComponent';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { MenuItem } from '@mui/material';
import type { Choice } from '@restgenerated/models/Choice';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { CreatedByAutocompleteRestFilter } from '@shared/autocompletes/CreatedByAutocompleteRestFilter';
import { ProgramAutocompleteRestFilter } from '@shared/autocompletes/ProgramAutocompleteRestFilter';
import { useQuery } from '@tanstack/react-query';
import { PROGRAM_STATE_FILTER } from '@utils/constants';
import { createHandleApplyFilterChange } from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  ResponsiveGrid,
  ResponsiveGridContainer,
  responsiveValue,
} from 'src/responsive';

interface FeedbackFiltersProps {
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  filter;
}
const FeedbackFilters = ({
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  filter,
}: FeedbackFiltersProps): ReactElement => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { isAllPrograms } = useBaseUrl();

  const { data: issueTypeChoices, isLoading: choicesLoading } = useQuery<
    Choice[]
  >({
    queryKey: restQueryKey(RestService.restChoicesFeedbackIssueTypeList),
    queryFn: () => RestService.restChoicesFeedbackIssueTypeList(),
  });

  const { handleFilterChange, applyFilterChanges, clearFilter } =
    createHandleApplyFilterChange(
      initialFilter,
      navigate,
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
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <ResponsiveGridContainer spacing={3} sx={{ alignItems: 'flex-end' }}>
        <ResponsiveGrid size="quarter">
          <SearchTextField
            value={filter.feedbackId}
            label="Search"
            onChange={(e) => handleFilterChange('feedbackId', e.target.value)}
            data-cy="filters-search"
          />
        </ResponsiveGrid>
        {isAllPrograms && (
          <ResponsiveGrid size="quarter">
            <ProgramAutocompleteRestFilter
              filter={filter}
              name="program"
              value={filter.program}
              setFilter={setFilter}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
            />
          </ResponsiveGrid>
        )}
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) => handleFilterChange('issueType', e.target.value)}
            label={t('Issue Type')}
            value={filter.issueType}
            data-cy="filters-issue-type"
          >
            {issueTypeChoices?.map((issueType) => (
              <MenuItem key={issueType.value} value={issueType.value}>
                {issueType.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <CreatedByAutocompleteRestFilter
            name="createdBy"
            filter={filter}
            value={filter.createdBy}
            label={t('Created by')}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            additionalVariables={{ isFeedbackCreator: true }}
          />
        </ResponsiveGrid>
        {!isAllPrograms && (
          <ResponsiveGrid
            size="quarter"
            sx={{ display: responsiveValue('none', 'block') }}
          />
        )}
        <ResponsiveGrid size="quarter" mobileSize="half">
          <DatePickerFilter
            topLabel={t('Creation Date')}
            label="From"
            onChange={(date) => handleFilterChange('createdAtBefore', date)}
            value={filter.createdAtBefore}
            dataCy="filters-creation-date-from"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <DatePickerFilter
            label={t('To')}
            onChange={(date) => handleFilterChange('createdAtAfter', date)}
            value={filter.createdAtAfter}
            dataCy="filters-creation-date-to"
          />
        </ResponsiveGrid>
        {isAllPrograms && (
          <ResponsiveGrid size="quarter">
            <SelectFilter
              onChange={(e) =>
                handleFilterChange('programState', e.target.value)
              }
              label={t('Programme State')}
              value={filter.programState}
              fullWidth
              disableClearable
              data-cy="filters-program-state"
            >
              <MenuItem value={PROGRAM_STATE_FILTER.ACTIVE}>
                {t('Active Programmes')}
              </MenuItem>
              <MenuItem value={PROGRAM_STATE_FILTER.ALL}>
                {t('All Programmes')}
              </MenuItem>
            </SelectFilter>
          </ResponsiveGrid>
        )}
      </ResponsiveGridContainer>
    </FiltersSection>
  );
};

export default withErrorBoundary(FeedbackFilters, 'FeedbackFilters');
