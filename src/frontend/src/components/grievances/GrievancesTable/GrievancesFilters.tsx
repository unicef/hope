import {
  isShowIssueType,
  SYSTEM_GENERATED_ISSUE_TYPES,
} from '@components/grievances/utils/createGrievanceUtils';
import { DatePickerFilter } from '@core/DatePickerFilter';
import { DocumentSearchField } from '@core/DocumentSearchField';
import { FiltersSection } from '@core/FiltersSection';
import { NumberTextField } from '@core/NumberTextField';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { AccountBalance } from '@mui/icons-material';
import { MenuItem } from '@mui/material';
import {
  ResponsiveGridContainer,
  ResponsiveGrid,
  responsiveValue,
} from 'src/responsive';
import type { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import { AdminAreaAutocomplete } from '@shared/autocompletes/AdminAreaAutocomplete';
import { AssigneeAutocompleteRestFilter } from '@shared/autocompletes/AssigneeAutocompleteRestFilter';
import { CreatedByAutocompleteRestFilter } from '@shared/autocompletes/CreatedByAutocompleteRestFilter';
import { LanguageAutocompleteRestFilter } from '@shared/autocompletes/LanguageAutocompleteRestFilter';
import { ProgramAutocompleteRestFilter } from '@shared/autocompletes/ProgramAutocompleteRestFilter';
import { RdiAutocompleteRestFilter } from '@shared/autocompletes/RdiAutocompleteRestFilter';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_TICKETS_TYPES,
  GrievanceStatuses,
  GrievanceTypes,
} from '@utils/constants';
import { createHandleApplyFilterChange } from '@utils/utils';
import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { ProgramStatusEnum } from '@restgenerated/models/ProgramStatusEnum';
import { useDocumentTypeChoices } from '@hooks/useDocumentTypeChoices';

interface GrievancesFiltersProps {
  filter;
  choicesData: GrievanceChoices;
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
}: GrievancesFiltersProps): ReactElement => {
  const { t } = useTranslation();
  const { isAllPrograms } = useBaseUrl();
  const { data: documentTypeChoices } = useDocumentTypeChoices();
  const navigate = useNavigate();
  const location = useLocation();

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

  const issueTypeDict = useArrayToDict(
    choicesData?.grievanceTicketIssueTypeChoices,
    'category',
    '*',
  );

  const isUserGeneratedTab =
    filter.grievanceType ===
    GrievanceTypes[GRIEVANCE_TICKETS_TYPES.userGenerated];

  const categoryChoices = useMemo(() => {
    if (isUserGeneratedTab)
      return choicesData.grievanceTicketFilterCategoryChoices;
    // Data Change is a manual category, but it also owns a system-generated issue type
    // (Biometric Photo Error), so it has to be selectable on the system tab too.
    const dataChangeCategory = choicesData.grievanceTicketCategoryChoices?.find(
      (item) => item.value?.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE,
    );
    return dataChangeCategory
      ? [
          ...choicesData.grievanceTicketSystemCategoryChoices,
          dataChangeCategory,
        ]
      : choicesData.grievanceTicketSystemCategoryChoices;
  }, [choicesData, isUserGeneratedTab]);

  const showIssueType = isShowIssueType(filter.category);

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

  const subCategoriesObj = issueTypeDict[filter.category]?.subCategories || [];

  // Transform to array of { name, value }
  const subcategories = Object.entries(subCategoriesObj)
    .map(([value, name]) => ({
      name,
      value,
    }))
    // Data Change shows on both tabs, so split its issue types by who creates them.
    .filter(({ value }) => {
      if (filter.category?.toString() !== GRIEVANCE_CATEGORIES.DATA_CHANGE)
        return true;
      const isSystemIssueType = SYSTEM_GENERATED_ISSUE_TYPES.includes(value);
      return isUserGeneratedTab ? !isSystemIssueType : isSystemIssueType;
    });

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <ResponsiveGridContainer
        spacing={3}
        sx={{
          alignItems: 'flex-end',
        }}
      >
        <ResponsiveGrid size="quarter">
          <SearchTextField
            value={filter.search}
            label="Search"
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filters-search"
          />
        </ResponsiveGrid>
        <DocumentSearchField
          onChange={handleFilterChange}
          type={filter.documentType}
          number={filter.documentNumber}
          choices={documentTypeChoices}
        />
        {isAllPrograms && (
          <ResponsiveGrid size="quarter">
            <ProgramAutocompleteRestFilter
              filter={filter}
              name="program"
              value={filter.program}
              status={[ProgramStatusEnum.ACTIVE]}
              setFilter={setFilter}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
            />
          </ResponsiveGrid>
        )}
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            label={t('Status')}
            value={filter.status}
            fullWidth
            data-cy="filters-status"
          >
            {choicesData.grievanceTicketStatusChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
        <ResponsiveGrid size="sixth">
          <SearchTextField
            value={filter.fsp}
            label="FSP"
            icon={<AccountBalance style={{ color: '#5f6368' }} />}
            fullWidth
            onChange={(e) => handleFilterChange('fsp', e.target.value)}
            data-cy="filters-fsp"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="sixth" mobileSize="half">
          <DatePickerFilter
            topLabel={t('Creation Date')}
            placeholder="From"
            onChange={(date) => handleFilterChange('createdAtBefore', date)}
            value={filter.createdAtBefore}
            fullWidth
            dataCy="filters-creation-date-from"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="sixth" mobileSize="half">
          <DatePickerFilter
            placeholder="To"
            onChange={(date) => handleFilterChange('createdAtAfter', date)}
            value={filter.createdAtAfter}
            fullWidth
            dataCy="filters-creation-date-to"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) => handleFilterChange('category', e.target.value)}
            label={t('Category')}
            value={filter.category?.toString() ?? ''}
            fullWidth
            data-cy="filters-category"
          >
            {categoryChoices.map((item) => (
              <MenuItem key={item.value} value={item.value?.toString()}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
        {showIssueType && (
          <ResponsiveGrid size="sixth">
            <SelectFilter
              onChange={(e) => handleFilterChange('issueType', e.target.value)}
              label="Issue Type"
              value={filter.issueType}
              fullWidth
            >
              {subcategories.map((item) => (
                <MenuItem key={item.value} value={item.value}>
                  {item.name as string}
                </MenuItem>
              ))}
            </SelectFilter>
          </ResponsiveGrid>
        )}
        <ResponsiveGrid size="quarter">
          <AssigneeAutocompleteRestFilter
            filter={filter}
            label={t('Assigned To')}
            name="assignedTo"
            value={filter.assignedTo}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy="filters-assignee"
          />
        </ResponsiveGrid>
        {selectedTab === GRIEVANCE_TICKETS_TYPES.userGenerated && (
          <ResponsiveGrid size="quarter">
            <CreatedByAutocompleteRestFilter
              filter={filter}
              name="createdBy"
              value={filter.createdBy}
              setFilter={setFilter}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
              additionalVariables={{ isTicketCreator: true }}
            />
          </ResponsiveGrid>
        )}
        {selectedTab === GRIEVANCE_TICKETS_TYPES.systemGenerated && (
          <ResponsiveGridContainer
            spacing={3}
            sx={{
              alignItems: 'flex-end',
              width: responsiveValue('100%', 'auto'),
            }}
          >
            <ResponsiveGrid size="half" mobileSize="half">
              <NumberTextField
                topLabel={t('Similarity Score')}
                value={filter.scoreMin}
                placeholder="From"
                onChange={(e) => handleFilterChange('scoreMin', e.target.value)}
                data-cy="filters-similarity-score-from"
                fullWidth
              />
            </ResponsiveGrid>
            <ResponsiveGrid size="half" mobileSize="half">
              <NumberTextField
                value={filter.scoreMax}
                placeholder="To"
                onChange={(e) => handleFilterChange('scoreMax', e.target.value)}
                data-cy="filters-similarity-score-to"
                fullWidth
              />
            </ResponsiveGrid>
          </ResponsiveGridContainer>
        )}
        {!isAllPrograms && (
          <ResponsiveGrid size="quarter">
            <RdiAutocompleteRestFilter
              filter={filter}
              name="registrationDataImport"
              value={filter.registrationDataImport}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
              setFilter={setFilter}
            />
          </ResponsiveGrid>
        )}
        <ResponsiveGrid size="quarter">
          <LanguageAutocompleteRestFilter
            filter={filter}
            name="preferredLanguage"
            value={filter.preferredLanguage}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            setFilter={setFilter}
            dataCy="filters-preferred-language"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) => handleFilterChange('priority', e.target.value)}
            label={t('Priority')}
            value={filter.priority}
            data-cy="filters-priority"
            fullWidth
          >
            {updatedPriorityChoices?.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
        <ResponsiveGrid size="sixth">
          <SelectFilter
            onChange={(e) => handleFilterChange('urgency', e.target.value)}
            label={t('Urgency')}
            value={filter.urgency}
            data-cy="filters-urgency"
            fullWidth
          >
            {updatedUrgencyChoices?.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
        {selectedTab === GRIEVANCE_TICKETS_TYPES.userGenerated && (
          <ResponsiveGrid size="quarter">
            <SelectFilter
              onChange={(e) =>
                handleFilterChange('submissionChannel', e.target.value)
              }
              label={t('Submission Channel')}
              value={filter.submissionChannel}
              data-cy="filters-submission-channel"
              fullWidth
            >
              {choicesData.grievanceTicketManualSubmissionChannelChoices?.map(
                (item) => (
                  <MenuItem key={item.value} value={item.value}>
                    {item.name}
                  </MenuItem>
                ),
              )}
            </SelectFilter>
          </ResponsiveGrid>
        )}
        <ResponsiveGrid size="sixth">
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('grievanceStatus', e.target.value)
            }
            label={undefined}
            value={filter.grievanceStatus}
            fullWidth
            disableClearable
            data-cy="filters-active-tickets"
          >
            <MenuItem value={GrievanceStatuses.Active}>
              {t('Active Tickets')}
            </MenuItem>
            <MenuItem value={GrievanceStatuses.All}>
              {t('All Tickets')}
            </MenuItem>
          </SelectFilter>
        </ResponsiveGrid>
        {selectedTab === GRIEVANCE_TICKETS_TYPES.systemGenerated && (
          <ResponsiveGrid size="sixth">
            <SelectFilter
              onChange={(e) => handleFilterChange('areaScope', e.target.value)}
              label={t('Ticket Type')}
              value={filter.areaScope}
              fullWidth
              disableClearable
              data-cy="filters-area-scope"
            >
              <MenuItem value="cross-area">{t('Cross-Area Tickets')}</MenuItem>
              <MenuItem value="all">{t('All Tickets')}</MenuItem>
            </SelectFilter>
          </ResponsiveGrid>
        )}
        <ResponsiveGrid size="quarter">
          <AdminAreaAutocomplete
            level={1}
            filter={filter}
            name="admin1"
            value={filter.admin1}
            disabled={filter.admin2}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy="filters-admin-level-1"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <AdminAreaAutocomplete
            level={2}
            filter={filter}
            name="admin2"
            value={filter.admin2}
            disabled={filter.admin1}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy="filters-admin-level-2"
          />
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </FiltersSection>
  );
};
