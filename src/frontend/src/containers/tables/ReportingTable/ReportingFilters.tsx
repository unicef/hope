import { Checkbox, FormControlLabel, Grid2 as Grid, MenuItem } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { DatePickerFilter } from '@components/core/DatePickerFilter';
import { FiltersSection } from '@components/core/FiltersSection';
import { SelectFilter } from '@components/core/SelectFilter';
import { createHandleApplyFilterChange } from '@utils/utils';
import { ReactElement } from 'react';

interface ReportingFiltersProps {
  filter;
  choicesData;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

export function ReportingFilters({
  filter,
  choicesData,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: ReportingFiltersProps): ReactElement {
  const { t } = useTranslation();
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

  return (
    <FiltersSection
      applyHandler={handleApplyFilter}
      clearHandler={handleClearFilter}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            label={t('Report Type')}
            onChange={(e) => handleFilterChange('type', e.target.value)}
            value={filter.type}
            dataCy="report-type-filter"
          >
            {choicesData.reportTypesChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            dataCy="report-created-from-filter"
            topLabel={t('Creation Date')}
            placeholder={t('From')}
            onChange={(date) => handleFilterChange('createdFrom', date)}
            value={filter.createdFrom}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            dataCy="report-created-to-filter"
            placeholder={t('To')}
            onChange={(date) => handleFilterChange('createdTo', date)}
            value={filter.createdTo}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            dataCy="report-status-filter"
            label="Status"
            onChange={(e) => handleFilterChange('status', e.target.value)}
            value={filter.status}
          >
            {choicesData.reportStatusChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 12 }}>
          <FormControlLabel
            control={
              <Checkbox
                data-cy="report-only-my-filter"
                checked={filter.onlyMy}
                onChange={(_e, checked) =>
                  handleFilterChange('onlyMy', checked)
                }
                value={filter.onlyMy}
                color="primary"
              />
            }
            label="See my reports only"
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
