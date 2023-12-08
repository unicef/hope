import { Grid, MenuItem } from '@material-ui/core';
import { AccountBalance } from '@material-ui/icons';
import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import {
  GrievancesChoiceDataQuery,
  useGrievanceTicketAreaScopeQuery,
} from '../../../__generated__/graphql';
import { useArrayToDict } from '../../../hooks/useArrayToDict';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { AdminAreaAutocomplete } from '../../../shared/autocompletes/AdminAreaAutocomplete';
import { AssigneeAutocomplete } from '../../../shared/autocompletes/AssigneeAutocomplete';
import { CreatedByAutocomplete } from '../../../shared/autocompletes/CreatedByAutocomplete';
import { LanguageAutocomplete } from '../../../shared/autocompletes/LanguageAutocomplete';
import { ProgramAutocomplete } from '../../../shared/autocompletes/ProgramAutocomplete';
import { RdiAutocomplete } from '../../../shared/autocompletes/RdiAutocomplete';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_TICKETS_TYPES,
  GrievanceStatuses,
  GrievanceTypes,
} from '../../../utils/constants';
import { createHandleApplyFilterChange } from '../../../utils/utils';
import { DatePickerFilter } from '../../core/DatePickerFilter';
import { FiltersSection } from '../../core/FiltersSection';
import { NumberTextField } from '../../core/NumberTextField';
import { SearchTextField } from '../../core/SearchTextField';
import { SelectFilter } from '../../core/SelectFilter';

interface GrievancesFiltersProps {
  filter;
  choicesData: GrievancesChoiceDataQuery;
  selectedTab: number;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const GrievancesFilters = ({
  filter,
  choicesData,
  selectedTab,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: GrievancesFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const { isAllPrograms } = useBaseUrl();
  const history = useHistory();
  const location = useLocation();
  const { data: areaScopeData } = useGrievanceTicketAreaScopeQuery();

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

  const categoryChoices = useMemo(() => {
    return filter.grievanceType ===
      GrievanceTypes[GRIEVANCE_TICKETS_TYPES.userGenerated]
      ? choicesData.grievanceTicketManualCategoryChoices
      : choicesData.grievanceTicketSystemCategoryChoices;
  }, [choicesData, filter.grievanceType]);

  const showIssueType =
    filter.category === GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE ||
    filter.category === GRIEVANCE_CATEGORIES.DATA_CHANGE ||
    filter.category === GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT;

  const updatedPriorityChoices = useMemo(() => {
    const priorityChoices = choicesData.grievanceTicketPriorityChoices;
    return priorityChoices.map((item) => {
      if (item.value === 0) {
        return { ...item, value: 'Not Set' };
      }
      return item;
    });
  }, [choicesData.grievanceTicketPriorityChoices]);

  const updatedUrgencyChoices = useMemo(() => {
    const urgencyChoices = choicesData.grievanceTicketUrgencyChoices;
    return urgencyChoices
      .map((item) => {
        if (item.value === 0) {
          return { ...item, value: 'Not Set' };
        }
        return item;
      })
      .reverse();
  }, [choicesData.grievanceTicketUrgencyChoices]);

  const subCategories = issueTypeDict[filter.category]?.subCategories || [];

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid container item xs={6} spacing={0}>
          <Grid item xs={8}>
            <SearchTextField
              value={filter.search}
              label='Search'
              onChange={(e) => handleFilterChange('search', e.target.value)}
              data-cy='filters-search'
              borderRadius='4px 0px 0px 4px'
            />
          </Grid>
          <Grid container item xs={4}>
            <SelectFilter
              onChange={(e) => handleFilterChange('searchType', e.target.value)}
              label='Search Type'
              value={filter.searchType}
              borderRadius='0px 4px 4px 0px'
              data-cy='filters-search-type'
              fullWidth
              disableClearable
            >
              {choicesData?.grievanceTicketSearchTypesChoices?.map(
                ({ name, value }) => (
                  <MenuItem key={value} value={value}>
                    {name}
                  </MenuItem>
                ),
              )}
            </SelectFilter>
          </Grid>
        </Grid>
        {isAllPrograms && (
          <Grid item xs={3}>
            <ProgramAutocomplete
              filter={filter}
              name='program'
              value={filter.program}
              setFilter={setFilter}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
            />
          </Grid>
        )}
        <Grid container item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            label={t('Status')}
            value={filter.status}
            fullWidth
            data-cy='filters-status'
          >
            {choicesData.grievanceTicketStatusChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <SearchTextField
            value={filter.fsp}
            label='FSP'
            icon={<AccountBalance style={{ color: '#5f6368' }} />}
            fullWidth
            onChange={(e) => handleFilterChange('fsp', e.target.value)}
            data-cy='filters-fsp'
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            topLabel={t('Creation Date')}
            placeholder='From'
            onChange={(date) => handleFilterChange('createdAtRangeMin', date)}
            value={filter.createdAtRangeMin}
            fullWidth
            data-cy='filters-creation-date-from'
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            placeholder='To'
            onChange={(date) => handleFilterChange('createdAtRangeMax', date)}
            value={filter.createdAtRangeMax}
            fullWidth
            data-cy='filters-creation-date-to'
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('category', e.target.value)}
            label={t('Category')}
            value={filter.category}
            fullWidth
            data-cy='filters-category'
          >
            {categoryChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        {showIssueType && (
          <Grid item xs={3}>
            <SelectFilter
              onChange={(e) => handleFilterChange('issueType', e.target.value)}
              label='Issue Type'
              value={filter.issueType}
              fullWidth
            >
              {subCategories.map((item) => (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              ))}
            </SelectFilter>
          </Grid>
        )}
        <Grid item xs={3}>
          <AdminAreaAutocomplete
            filter={filter}
            name='admin2'
            value={filter.admin2}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy='filters-admin-level'
          />
        </Grid>
        <Grid item xs={3}>
          <AssigneeAutocomplete
            filter={filter}
            label={t('Assigned To')}
            name='assignedTo'
            value={filter.assignedTo}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy='filters-assignee'
          />
        </Grid>
        {selectedTab === GRIEVANCE_TICKETS_TYPES.userGenerated && (
          <Grid item xs={3}>
            <CreatedByAutocomplete
              filter={filter}
              name='createdBy'
              value={filter.createdBy}
              setFilter={setFilter}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
              additionalVariables={{ isTicketCreator: true }}
            />
          </Grid>
        )}
        {selectedTab === GRIEVANCE_TICKETS_TYPES.systemGenerated && (
          <Grid container item xs={6} spacing={3} alignItems='flex-end'>
            <Grid item xs={6}>
              <NumberTextField
                topLabel={t('Similarity Score')}
                value={filter.scoreMin}
                placeholder='From'
                onChange={(e) => handleFilterChange('scoreMin', e.target.value)}
                data-cy='filters-similarity-score-from'
                fullWidth
              />
            </Grid>
            <Grid item xs={6}>
              <NumberTextField
                value={filter.scoreMax}
                placeholder='To'
                onChange={(e) => handleFilterChange('scoreMax', e.target.value)}
                data-cy='filters-similarity-score-to'
                fullWidth
              />
            </Grid>
          </Grid>
        )}
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
            dataCy='filters-preferred-language'
          />
        </Grid>
        <Grid item container xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('priority', e.target.value)}
            label={t('Priority')}
            value={filter.priority}
            data-cy='filters-priority'
            fullWidth
          >
            {updatedPriorityChoices?.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item container xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('urgency', e.target.value)}
            label={t('Urgency')}
            value={filter.urgency}
            data-cy='filters-urgency'
            fullWidth
          >
            {updatedUrgencyChoices?.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item container xs={3}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('grievanceStatus', e.target.value)
            }
            label={undefined}
            value={filter.grievanceStatus}
            fullWidth
            disableClearable
            data-cy='filters-active-tickets'
          >
            <MenuItem value={GrievanceStatuses.Active}>
              {t('Active Tickets')}
            </MenuItem>
            <MenuItem value={GrievanceStatuses.All}>
              {t('All Tickets')}
            </MenuItem>
          </SelectFilter>
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
        {selectedTab === GRIEVANCE_TICKETS_TYPES.systemGenerated &&
          areaScopeData?.crossAreaFilterAvailable && (
            <Grid item xs={3}>
              <SelectFilter
                onChange={(e) =>
                  handleFilterChange('areaScope', e.target.value)
                }
                label={t('Area Scope')}
                value={filter.areaScope}
                fullWidth
                disableClearable
                data-cy='filters-area-scope'
              >
                <MenuItem value='cross-area'>
                  {t('Cross-Area Tickets')}
                </MenuItem>
                <MenuItem value='all'>{t('All Tickets')}</MenuItem>
              </SelectFilter>
            </Grid>
          )}
      </Grid>
    </FiltersSection>
  );
};
