import ViewModuleRoundedIcon from '@mui/icons-material/ViewModuleRounded';
import { MenuItem } from '@mui/material';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { AssigneeAutocompleteRestFilter } from '@shared/autocompletes/AssigneeAutocompleteRestFilter';
import { createHandleApplyFilterChange } from '@utils/utils';
import { FiltersSection } from './FiltersSection';
import { SearchTextField } from './SearchTextField';
import { SelectFilter } from './SelectFilter';
import { useProgramContext } from 'src/programContext';
import type { ReactElement } from 'react';

interface ActivityLogPageFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export function ActivityLogPageFilters({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: ActivityLogPageFiltersProps): ReactElement {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

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

  const modules = {
    program: 'Programme',
    household: `${beneficiaryGroup?.groupLabel}`,
    individual: `${beneficiaryGroup?.memberLabel}`,
    grievanceticket: 'Grievance Tickets',
    paymentverificationplan: 'Payment Plan Payment Verification',
    targetpopulation: 'Target Population',
    registrationdataimport: 'Registration Data Import',
  };
  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <ResponsiveGridContainer spacing={3} sx={{ alignItems: 'center' }}>
        <ResponsiveGrid size="quarter">
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filters-search"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) => handleFilterChange('module', e.target.value)}
            label={t('Module')}
            value={filter.module}
            icon={<ViewModuleRoundedIcon />}
            SelectDisplayProps={{
              'data-cy': 'filters-residence-status',
            }}
            MenuProps={{
              'data-cy': 'filters-residence-status-options',
            }}
          >
            {Object.entries(modules)
              .sort()
              .map(([key, value]) => (
                <MenuItem key={key} value={key}>
                  {value}
                </MenuItem>
              ))}
          </SelectFilter>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <AssigneeAutocompleteRestFilter
            label={t('User')}
            filter={filter}
            name="userId"
            value={filter.userId}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </FiltersSection>
  );
}
