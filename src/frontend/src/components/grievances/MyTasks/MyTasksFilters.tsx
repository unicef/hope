import { isShowIssueType } from '@components/grievances/utils/createGrievanceUtils';
import { FiltersSection } from '@core/FiltersSection';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { useBaseUrl } from '@hooks/useBaseUrl';
import Grid from '@mui/material/Grid';
import { MenuItem } from '@mui/material';
import type { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import { ProgramAutocompleteRestFilter } from '@shared/autocompletes/ProgramAutocompleteRestFilter';
import { ProgramStatusEnum } from '@restgenerated/models/ProgramStatusEnum';
import { GrievanceStatuses } from '@utils/constants';
import { createHandleApplyFilterChange } from '@utils/utils';
import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';

interface MyTasksFiltersProps {
  filter;
  choicesData: GrievanceChoices;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

export const MyTasksFilters = ({
  filter,
  choicesData,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: MyTasksFiltersProps): ReactElement => {
  const { t } = useTranslation();
  const { isAllPrograms } = useBaseUrl();
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

  const issueTypeDict = useArrayToDict(
    choicesData?.grievanceTicketIssueTypeChoices,
    'category',
    '*',
  );

  // My Tasks is not split into user- and system-generated, so it offers every category.
  const categoryChoices = choicesData.grievanceTicketCategoryChoices;

  const showIssueType = isShowIssueType(filter.category);

  const subcategories = useMemo(() => {
    const subCategoriesObj =
      issueTypeDict[filter.category]?.subCategories || {};
    return Object.entries(subCategoriesObj).map(([value, name]) => ({
      name,
      value,
    }));
  }, [issueTypeDict, filter.category]);

  const updatedPriorityChoices = useMemo(
    () =>
      choicesData.grievanceTicketPriorityChoices.map((item) =>
        item.value === 0 ? { ...item, value: 'Not Set' } : item,
      ),
    [choicesData.grievanceTicketPriorityChoices],
  );

  const updatedUrgencyChoices = useMemo(
    () =>
      choicesData.grievanceTicketUrgencyChoices
        .map((item) =>
          item.value === 0 ? { ...item, value: 'Not Set' } : item,
        )
        .reverse(),
    [choicesData.grievanceTicketUrgencyChoices],
  );

  return (
    <FiltersSection
      clearHandler={clearFilter}
      applyHandler={applyFilterChanges}
    >
      <Grid
        container
        spacing={3}
        sx={{
          alignItems: 'flex-end',
        }}
      >
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            value={filter.search}
            label="Search"
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filters-search"
          />
        </Grid>
        {isAllPrograms && (
          <Grid size={{ xs: 3 }}>
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
          </Grid>
        )}
        <Grid size={{ xs: 3 }}>
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
        </Grid>
        {showIssueType && (
          <Grid size={{ xs: 3 }}>
            <SelectFilter
              onChange={(e) => handleFilterChange('issueType', e.target.value)}
              label="Issue Type"
              value={filter.issueType}
              fullWidth
              data-cy="filters-issue-type"
            >
              {subcategories.map((item) => (
                <MenuItem key={item.value} value={item.value}>
                  {item.name as string}
                </MenuItem>
              ))}
            </SelectFilter>
          </Grid>
        )}
        <Grid size={{ xs: 3 }}>
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
        </Grid>
        <Grid size={{ xs: 3 }}>
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
        </Grid>
        <Grid size={{ xs: 2 }}>
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
        </Grid>
        {/* The overdue emails deep-link with ?overdue=true; showing it here is what tells the
            recipient why the list is short, and lets them switch it off. */}
        <Grid size={{ xs: 2 }}>
          <SelectFilter
            onChange={(e) =>
              // Clearing has to write '' rather than false: `overdue=false` is a real backend
              // filter meaning "not overdue", which is not what switching this off should do.
              handleFilterChange(
                'overdue',
                e.target.value === 'true' ? true : '',
              )
            }
            label={undefined}
            // getFilterFromQueryParams turns ?overdue=true into a boolean, so normalise here.
            value={filter.overdue ? 'true' : ''}
            fullWidth
            disableClearable
            data-cy="filters-overdue"
          >
            <MenuItem value="">{t('All Tickets')}</MenuItem>
            <MenuItem value="true">{t('Overdue Only')}</MenuItem>
          </SelectFilter>
        </Grid>
      </Grid>
    </FiltersSection>
  );
};
