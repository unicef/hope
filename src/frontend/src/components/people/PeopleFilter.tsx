import { Grid, MenuItem } from '@mui/material';
import CakeIcon from '@mui/icons-material/Cake';
import FlashOnIcon from '@mui/icons-material/FlashOn';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  DataCollectingTypeType,
  IndividualChoiceDataQuery,
  ProgramNode,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { AdminAreaAutocomplete } from '@shared/autocompletes/AdminAreaAutocomplete';
import { individualTableOrderOptions } from '@utils/constants';
import { createHandleApplyFilterChange } from '@utils/utils';
import { DatePickerFilter } from '@core/DatePickerFilter';
import { FiltersSection } from '@core/FiltersSection';
import { NumberTextField } from '@core/NumberTextField';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { useProgramContext } from '../../programContext';

interface PeopleFilterProps {
  filter;
  programs?: ProgramNode[];
  choicesData: IndividualChoiceDataQuery;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  isOnPaper?: boolean;
}

export function PeopleFilter({
  filter,
  programs,
  choicesData,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  isOnPaper = true,
}: PeopleFilterProps): React.ReactElement {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { isAllPrograms } = useBaseUrl();
  const { selectedProgram } = useProgramContext();

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

  // Show admin area filter only for social programs
  const showAdminAreaFilter =
    selectedProgram?.dataCollectingType?.type?.toUpperCase() ===
    DataCollectingTypeType.Social;

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
      isOnPaper={isOnPaper}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="ind-filters-search"
          />
        </Grid>
        <Grid container item xs={6} spacing={3}>
          <Grid item xs={6}>
            <SelectFilter
              onChange={(e) =>
                handleFilterChange('documentType', e.target.value)
              }
              label={t('Document Type')}
              value={filter.documentType}
              borderRadius="0px 4px 4px 0px"
              data-cy="filters-document-type"
              fullWidth
              disableClearable
            >
              {choicesData?.documentTypeChoices.map(({ name, value }) => (
                <MenuItem key={value} value={value}>
                  {name}
                </MenuItem>
              ))}
            </SelectFilter>
          </Grid>
          <Grid item xs={6}>
            <SearchTextField
              label={t('Document number')}
              value={filter.documentNumber}
              onChange={(e) =>
                handleFilterChange('documentNumber', e.target.value)
              }
              data-cy="filters-document-number"
            />
          </Grid>
        </Grid>
        {isAllPrograms && (
          <Grid item xs={2}>
            <SelectFilter
              onChange={(e) => handleFilterChange('program', e.target.value)}
              label={t('Programme')}
              value={filter.program}
              fullWidth
              icon={<FlashOnIcon />}
              data-cy="filters-program"
            >
              {programs.map((program) => (
                <MenuItem key={program.id} value={program.id}>
                  {program.name}
                </MenuItem>
              ))}
            </SelectFilter>
          </Grid>
        )}
        {showAdminAreaFilter && (
          <>
            <Grid item xs={2}>
              <AdminAreaAutocomplete
                level={1}
                name="admin1"
                value={filter.admin1}
                disabled={filter.admin2}
                setFilter={setFilter}
                filter={filter}
                initialFilter={initialFilter}
                appliedFilter={appliedFilter}
                setAppliedFilter={setAppliedFilter}
                dataCy="ind-filters-admin1"
              />
            </Grid>
            <Grid item xs={2}>
              <AdminAreaAutocomplete
                level={2}
                name="admin2"
                value={filter.admin2}
                disabled={filter.admin1}
                setFilter={setFilter}
                filter={filter}
                initialFilter={initialFilter}
                appliedFilter={appliedFilter}
                setAppliedFilter={setAppliedFilter}
                dataCy="ind-filters-admin2"
              />
            </Grid>
          </>
        )}
        <Grid item xs={2}>
          <SelectFilter
            onChange={(e) => handleFilterChange('sex', e.target.value)}
            value={filter.sex}
            label={t('Gender')}
            data-cy="ind-filters-gender"
            fullWidth
          >
            <MenuItem value="FEMALE">{t('Female')}</MenuItem>
            <MenuItem value="MALE">{t('Male')}</MenuItem>
          </SelectFilter>
        </Grid>
        <Grid item xs={2}>
          <NumberTextField
            fullWidth
            topLabel={t('Age')}
            placeholder={t('From')}
            value={filter.ageMin}
            data-cy="ind-filters-age-from"
            onChange={(e) => {
              if (e.target.value < 0 || e.target.value > 120) return;
              handleFilterChange('ageMin', e.target.value);
            }}
            icon={<CakeIcon />}
          />
        </Grid>
        <Grid item xs={2}>
          <NumberTextField
            fullWidth
            placeholder={t('To')}
            value={filter.ageMax}
            data-cy="ind-filters-age-to"
            onChange={(e) => {
              if (e.target.value < 0 || e.target.value > 120) return;
              handleFilterChange('ageMax', e.target.value);
            }}
            icon={<CakeIcon />}
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('flags', e.target.value)}
            label={t('Flags')}
            multiple
            fullWidth
            value={filter.flags}
            data-cy="ind-filters-flags"
          >
            {choicesData?.flagChoices.map((each, index) => (
              <MenuItem
                key={each.value}
                value={each.value}
                data-cy={`select-option-${index}`}
              >
                {each.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('orderBy', e.target.value)}
            label={t('Sort by')}
            value={filter.orderBy}
            fullWidth
            data-cy="ind-filters-order-by"
            disableClearable
          >
            {individualTableOrderOptions.map((order) => (
              <MenuItem key={order.value} value={order.value}>
                {order.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={2}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            label={t('Status')}
            value={filter.status}
            data-cy="ind-filters-status"
          >
            <MenuItem key="active" value="ACTIVE">
              Active
            </MenuItem>
            <MenuItem key="duplicate" value="DUPLICATE">
              Duplicate
            </MenuItem>
            <MenuItem key="withdrawn" value="WITHDRAWN">
              Withdrawn
            </MenuItem>
          </SelectFilter>
        </Grid>
        <Grid item xs={2}>
          <DatePickerFilter
            topLabel={t('Registration Date')}
            placeholder={t('From')}
            onChange={(date) =>
              handleFilterChange('lastRegistrationDateMin', date)
            }
            value={filter.lastRegistrationDateMin}
            dataCy="ind-filters-reg-date-from"
          />
        </Grid>
        <Grid item xs={2}>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) =>
              handleFilterChange('lastRegistrationDateMax', date)
            }
            value={filter.lastRegistrationDateMax}
            dataCy="ind-filters-reg-date-to"
          />
        </Grid>
        {isAllPrograms && (
          <Grid item xs={2}>
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
}
