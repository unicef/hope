import { DocumentSearchField } from '@core/DocumentSearchField';
import { FiltersSection } from '@core/FiltersSection';
import { NumberTextField } from '@core/NumberTextField';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { ProgramNode } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import AssignmentIndRoundedIcon from '@mui/icons-material/AssignmentIndRounded';
import FlashOnIcon from '@mui/icons-material/FlashOn';
import GroupIcon from '@mui/icons-material/Group';
import { Grid2 as Grid, MenuItem } from '@mui/material';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';
import { AdminAreaAutocomplete } from '@shared/autocompletes/AdminAreaAutocomplete';
import { generateTableOrderOptionsGroup } from '@utils/constants';
import { createHandleApplyFilterChange } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';

interface HouseholdFiltersProps {
  filter;
  programs?: ProgramNode[];
  choicesData: HouseholdChoices;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  isOnPaper?: boolean;
}

export function HouseholdFilters({
  filter,
  programs,
  choicesData,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  isOnPaper = true,
}: HouseholdFiltersProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const navigate = useNavigate();
  const location = useLocation();
  const { isAllPrograms } = useBaseUrl();
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
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
      isOnPaper={isOnPaper}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="hh-filters-search"
          />
        </Grid>
        <DocumentSearchField
          onChange={handleFilterChange}
          type={filter.documentType}
          number={filter.documentNumber}
          choices={choicesData?.documentTypeChoices}
        />
        {isAllPrograms && (
          <Grid size={{ xs: 3 }}>
            <SelectFilter
              onChange={(e) => handleFilterChange('program', e.target.value)}
              label={t('Programme')}
              value={filter.program}
              fullWidth
              icon={<FlashOnIcon />}
              data-cy="hh-filters-program"
            >
              {programs?.map((program) => (
                <MenuItem key={program.id} value={program.id}>
                  {program.name}
                </MenuItem>
              ))}
            </SelectFilter>
          </Grid>
        )}
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
          <NumberTextField
            topLabel={`${beneficiaryGroup?.groupLabel} ${t('Size')}`}
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
            disableClearable
          >
            {householdTableOrderOptions?.map((order) => (
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
        {isAllPrograms && (
          <Grid size={{ xs: 3 }}>
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
              <MenuItem value="active">{t('Active Programmes')}</MenuItem>
              <MenuItem value="all">{t('All Programmes')}</MenuItem>
            </SelectFilter>
          </Grid>
        )}
        <Grid size={{ xs: 3 }}>
          <AdminAreaAutocomplete
            name="admin1"
            level={1}
            value={filter.admin1}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            disabled={filter.admin2}
            dataCy="hh-filters-admin1"
          />
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
            disabled={filter.admin1}
            dataCy="hh-filters-admin2"
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
