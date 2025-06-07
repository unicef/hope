import AssignmentIndRoundedIcon from '@mui/icons-material/AssignmentIndRounded';
import GroupIcon from '@mui/icons-material/Group';
import { Grid2 as Grid, MenuItem } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { AdminAreaAutocomplete } from '@shared/autocompletes/AdminAreaAutocomplete';
import { generateTableOrderOptionsGroup } from '@utils/constants';
import { createHandleApplyFilterChange } from '@utils/utils';
import { FiltersSection } from '@core/FiltersSection';
import { NumberTextField } from '@core/NumberTextField';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';

interface LookUpHouseholdFiltersCommunicationProps {
  filter;
  choicesData: HouseholdChoices;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

export function LookUpHouseholdFiltersCommunication({
  filter,
  choicesData,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: LookUpHouseholdFiltersCommunicationProps): ReactElement {
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

  const householdTableOrderOptions =
    generateTableOrderOptionsGroup(beneficiaryGroup);

  return (
    <FiltersSection
      applyHandler={handleApplyFilter}
      clearHandler={handleClearFilter}
      isOnPaper={false}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            fullWidth
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="hh-filters-search"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('residenceStatus', e.target.value)
            }
            label={t('Residence Status')}
            fullWidth
            value={filter.residenceStatus}
            icon={<AssignmentIndRoundedIcon />}
            data-cy="hh-filters-residence-status"
          >
            {choicesData.residenceStatusChoices?.map((status) => (
              <MenuItem key={status.value} value={status.value}>
                {status.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <AdminAreaAutocomplete
            name="admin2"
            level={2}
            value={filter.admin2}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy="hh-filters-admin2"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <NumberTextField
            topLabel={`${beneficiaryGroup?.groupLabel} Size`}
            value={filter.householdSizeMin}
            placeholder={t('From')}
            icon={<GroupIcon />}
            fullWidth
            onChange={(e) =>
              handleFilterChange('householdSizeMin', e.target.value)
            }
            data-cy="hh-filters-household-size-from"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <NumberTextField
            value={filter.householdSizeMax}
            placeholder={t('To')}
            icon={<GroupIcon />}
            fullWidth
            onChange={(e) =>
              handleFilterChange('householdSizeMax', e.target.value)
            }
            data-cy="hh-filters-household-size-to"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) => handleFilterChange('orderBy', e.target.value)}
            label={t('Sort by')}
            value={filter.orderBy}
            data-cy="hh-filters-order-by"
          >
            {householdTableOrderOptions.map((order) => (
              <MenuItem key={order.value} value={order.value}>
                {order.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) => handleFilterChange('withdrawn', e.target.value)}
            label={t('Status')}
            value={filter.withdrawn}
            data-cy="hh-filters-status"
          >
            <MenuItem key="all" value="null">
              All
            </MenuItem>
            <MenuItem key="active" value="false">
              Active
            </MenuItem>
            <MenuItem key="inactive" value="true">
              Withdrawn
            </MenuItem>
          </SelectFilter>
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
