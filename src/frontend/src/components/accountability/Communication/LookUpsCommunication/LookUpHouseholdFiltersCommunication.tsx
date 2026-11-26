import { FiltersSection } from '@core/FiltersSection';
import { NumberTextField } from '@core/NumberTextField';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import AssignmentIndRoundedIcon from '@mui/icons-material/AssignmentIndRounded';
import GroupIcon from '@mui/icons-material/Group';
import { MenuItem } from '@mui/material';
import type { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';
import { AdminAreaAutocomplete } from '@shared/autocompletes/AdminAreaAutocomplete';
import { generateTableOrderOptionsGroup } from '@utils/constants';
import { createHandleApplyFilterChange } from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

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
      <ResponsiveGridContainer spacing={3} sx={{ alignItems: 'flex-end' }}>
        <ResponsiveGrid size="quarter">
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            fullWidth
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="hh-filters-search"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) => handleFilterChange('orderBy', e.target.value)}
            label={t('Sort by')}
            value={filter.orderBy}
            data-cy="hh-filters-order-by"
          >
            {householdTableOrderOptions?.map((order) => (
              <MenuItem key={order.value} value={order.value}>
                {order.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
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
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </FiltersSection>
  );
}
