import ViewModuleRoundedIcon from '@mui/icons-material/ViewModuleRounded';
import { Grid2 as Grid, MenuItem } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { AssigneeAutocomplete } from '@shared/autocompletes/AssigneeAutocomplete';
import { createHandleApplyFilterChange } from '@utils/utils';
import { FiltersSection } from './FiltersSection';
import { SearchTextField } from './SearchTextField';
import { SelectFilter } from './SelectFilter';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';

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
      <Grid container alignItems="center" spacing={3}>
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filters-search"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
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
        </Grid>
        <Grid size={{ xs: 3 }}>
          <AssigneeAutocomplete
            label={t('User')}
            filter={filter}
            name="userId"
            value={filter.userId}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
