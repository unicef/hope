import { Grid, MenuItem } from '@mui/material';
import AssignmentIndRoundedIcon from '@material-ui/icons/AssignmentIndRounded';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import GroupIcon from '@material-ui/icons/Group';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import {
  HouseholdChoiceDataQuery,
  ProgramNode,
} from '../../__generated__/graphql';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { AdminAreaAutocomplete } from '../../shared/autocompletes/AdminAreaAutocomplete';
import { householdTableOrderOptions } from '../../utils/constants';
import { createHandleApplyFilterChange } from '../../utils/utils';
import { FiltersSection } from '../core/FiltersSection';
import { NumberTextField } from '../core/NumberTextField';
import { SearchTextField } from '../core/SearchTextField';
import { SelectFilter } from '../core/SelectFilter';

interface HouseholdFiltersProps {
  filter;
  programs?: ProgramNode[];
  choicesData: HouseholdChoiceDataQuery;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  isOnPaper?: boolean;
}

export const HouseholdFilters = ({
  filter,
  programs,
  choicesData,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  isOnPaper = true,
}: HouseholdFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();
  const { isAllPrograms } = useBaseUrl();
  const { handleFilterChange, applyFilterChanges, clearFilter } =
    createHandleApplyFilterChange(
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

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
      isOnPaper={isOnPaper}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid container item xs={6} spacing={0}>
          <Grid item xs={8}>
            <SearchTextField
              label={t('Search')}
              value={filter.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              data-cy="hh-filters-search"
            />
          </Grid>
          <Grid item xs={4}>
            <SelectFilter
              onChange={(e) => handleFilterChange('searchType', e.target.value)}
              label={t('Search Type')}
              value={filter.searchType}
              borderRadius="0px 4px 4px 0px"
              data-cy="filter-search-type"
              fullWidth
              disableClearable
            >
              {choicesData?.householdSearchTypesChoices.map(
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
            <SelectFilter
              onChange={(e) => handleFilterChange('program', e.target.value)}
              label={t('Programme')}
              value={filter.program}
              fullWidth
              icon={<FlashOnIcon />}
              data-cy="hh-filters-program"
            >
              {programs.map((program) => (
                <MenuItem key={program.id} value={program.id}>
                  {program.name}
                </MenuItem>
              ))}
            </SelectFilter>
          </Grid>
        )}
        <Grid item xs={3}>
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
        <Grid item xs={3}>
          <AdminAreaAutocomplete
            name="admin2"
            value={filter.admin2}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy="hh-filters-admin2"
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            topLabel={t('Household Size')}
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
        <Grid item xs={3}>
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
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('orderBy', e.target.value)}
            label={t('Sort by')}
            value={filter.orderBy}
            data-cy="hh-filters-order-by"
            disableClearable
          >
            {householdTableOrderOptions.map((order) => (
              <MenuItem key={order.value} value={order.value}>
                {order.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
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
          <Grid item xs={3}>
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
      </Grid>
    </FiltersSection>
  );
};
