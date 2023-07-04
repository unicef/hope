import { Grid, MenuItem } from '@material-ui/core';
import { AccountBalance } from '@material-ui/icons';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import moment from 'moment';
import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import {
  GrievancesChoiceDataQuery,
  ProgramNode,
} from '../../../__generated__/graphql';
import { useArrayToDict } from '../../../hooks/useArrayToDict';
import { AdminAreaAutocomplete } from '../../../shared/autocompletes/AdminAreaAutocomplete';
import { AssigneeAutocomplete } from '../../../shared/autocompletes/AssigneeAutocomplete';
import { LanguageAutocomplete } from '../../../shared/autocompletes/LanguageAutocomplete';
import { RdiAutocomplete } from '../../../shared/autocompletes/RdiAutocomplete';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_TICKETS_TYPES,
  GrievanceSearchTypes,
  GrievanceStatuses,
  GrievanceTypes,
  ISSUE_TYPE_CATEGORIES,
} from '../../../utils/constants';
import { createHandleApplyFilterChange } from '../../../utils/utils';
import { ClearApplyButtons } from '../../core/ClearApplyButtons';
import { ContainerWithBorder } from '../../core/ContainerWithBorder';
import { DatePickerFilter } from '../../core/DatePickerFilter';
import { NumberTextField } from '../../core/NumberTextField';
import { SearchTextField } from '../../core/SearchTextField';
import { SelectFilter } from '../../core/SelectFilter';

interface GrievancesFiltersProps {
  filter;
  choicesData: GrievancesChoiceDataQuery;
  programs: ProgramNode[];
  selectedTab: number;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const GrievancesFilters = ({
  filter,
  choicesData,
  programs,
  selectedTab,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: GrievancesFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();
  const isUserGenerated = location.pathname.indexOf('user-generated') !== -1;

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
    filter.category === ISSUE_TYPE_CATEGORIES.SENSITIVE_GRIEVANCE ||
    filter.category === ISSUE_TYPE_CATEGORIES.DATA_CHANGE ||
    filter.category === ISSUE_TYPE_CATEGORIES.GRIEVANCE_COMPLAINT;

  return (
    <ContainerWithBorder>
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
              label={undefined}
              value={filter.searchType}
              borderRadius='0px 4px 4px 0px'
              data-cy='filters-search-type'
              fullWidth
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
        </Grid>
        <Grid container item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            label={t('Status')}
            value={filter.status}
            fullWidth
            data-cy='filters-status'
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
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
            onChange={(date) =>
              handleFilterChange(
                'createdAtRangeMin',
                moment(date)
                  .set({ hour: 0, minute: 0 })
                  .toISOString(),
              )
            }
            value={filter.createdAtRangeMin}
            fullWidth
            data-cy='filters-creation-date-from'
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
        {showIssueType && (
          <Grid item>
            <SelectFilter
              onChange={(e) => handleFilterChange('issueType', e.target.value)}
              label='Issue Type'
              value={filter.issueType}
              fullWidth
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {issueTypeDict[
                GRIEVANCE_CATEGORIES[
                  filter.category.replace(/\s/g, '_').toUpperCase()
                ]
              ].subCategories.map((item) => {
                return (
                  <MenuItem key={item.value} value={item.value}>
                    {item.name}
                  </MenuItem>
                );
              })}
            </SelectFilter>
          </Grid>
        )}
        <Grid item xs={3}>
          <AdminAreaAutocomplete
            filter={filter}
            name='admin'
            value={filter.admin}
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
            name='assignedTo'
            value={filter.assignedTo}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy='filters-assignee'
          />
        </Grid>
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
            dataCy='filters-registration-data-import'
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
        <Grid item container xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('urgency', e.target.value)}
            label={t('Urgency')}
            value={filter.urgency}
            data-cy='filters-urgency'
            fullWidth
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
        {!isUserGenerated && (
          <Grid item xs={3}>
            <SelectFilter
              onChange={(e) => handleFilterChange('program', e.target.value)}
              label={t('Programme')}
              value={filter.program}
              icon={<FlashOnIcon />}
              fullWidth
              data-cy='hh-filters-program'
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
        <Grid item container xs={3}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('grievanceStatus', e.target.value)
            }
            label={undefined}
            value={filter.grievanceStatus}
            fullWidth
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
      </Grid>
      <ClearApplyButtons
        clearHandler={handleClearFilter}
        applyHandler={handleApplyFilter}
      />
    </ContainerWithBorder>
  );
};
