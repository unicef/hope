import withErrorBoundary from '@components/core/withErrorBoundary';
import { DatePickerFilter } from '@core/DatePickerFilter';
import { FiltersSection } from '@core/FiltersSection';
import { LoadingComponent } from '@core/LoadingComponent';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Grid2 as Grid, MenuItem } from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { CreatedByAutocompleteRestFilter } from '@shared/autocompletes/CreatedByAutocompleteRestFilter';
import { ProgramAutocompleteRestFilter } from '@shared/autocompletes/ProgramAutocompleteRestFilter';
import { useQuery } from '@tanstack/react-query';
import { createHandleApplyFilterChange } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';

interface FeedbackFiltersProps {
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  _filter;
}
const FeedbackFilters = ({
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  _filter,
}: FeedbackFiltersProps): ReactElement => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { businessArea } = useBaseUrl();
  const { isAllPrograms } = useBaseUrl();

  const { data: choicesData, isLoading: choicesLoading } = useQuery<any>({
    queryKey: ['businessAreasGrievanceTicketsChoices', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
        businessAreaSlug: businessArea,
      }),
  });

  const { handleFilterChange, applyFilterChanges, clearFilter } =
    createHandleApplyFilterChange(
      initialFilter,
      navigate,
      location,
      _filter,
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
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            value={_filter.feedbackId}
            label="Search"
            onChange={(e) => handleFilterChange('feedbackId', e.target.value)}
            data-cy="filters-search"
          />
        </Grid>
        {isAllPrograms && (
          <Grid size={{ xs: 3 }}>
            <ProgramAutocompleteRestFilter
              filter={_filter}
              name="program"
              value={_filter.program}
              setFilter={setFilter}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
            />
          </Grid>
        )}
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) => handleFilterChange('issueType', e.target.value)}
            label={t('Issue Type')}
            value={_filter.issueType}
            data-cy="filters-issue-type"
          >
            {choicesData?.feedbackIssueTypeChoices?.map((issueType) => (
              <MenuItem key={issueType.name} value={issueType.value}>
                {issueType.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <CreatedByAutocompleteRestFilter
            name="createdBy"
            filter={_filter}
            value={_filter.createdBy}
            label={t('Created by')}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            additionalVariables={{ isFeedbackCreator: true }}
          />
        </Grid>
        {!isAllPrograms && <Grid size={{ xs: 3 }} />}
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            topLabel={t('Creation Date')}
            label="From"
            onChange={(date) => handleFilterChange('createdAtBefore', date)}
            value={_filter.createdAtBefore}
            dataCy="filters-creation-date-from"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            label={t('To')}
            onChange={(date) => handleFilterChange('createdAtAfter', date)}
            value={_filter.createdAtAfter}
            dataCy="filters-creation-date-to"
          />
        </Grid>
        {isAllPrograms && (
          <Grid size={{ xs: 3 }}>
            <SelectFilter
              onChange={(e) =>
                handleFilterChange('programState', e.target.value)
              }
              label={t('Programme State')}
              value={_filter.programState}
              fullWidth
              disableClearable
              data-cy="filters-program-state"
            >
              <MenuItem value="active">{t('Active Programmes')}</MenuItem>
              <MenuItem value="all">{t('All Programmes')}</MenuItem>
            </SelectFilter>
          </Grid>
        )}
      </Grid>
    </FiltersSection>
  );
};

export default withErrorBoundary(FeedbackFilters, 'FeedbackFilters');
