import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { createHandleApplyFilterChange } from '@utils/utils';
import { Grid2 as Grid, MenuItem } from '@mui/material';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { NumberTextField } from '@core/NumberTextField';
import { DatePickerFilter } from '@core/DatePickerFilter';
import moment from 'moment/moment';
import { FiltersSection } from '@components/core/FiltersSection';

interface ProgramCyclesFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

const programCycleStatuses = [
  { value: 'ACTIVE', name: 'Active' },
  { value: 'DRAFT', name: 'Draft' },
  { value: 'FINISHED', name: 'Finished' },
];

export const ProgramCyclesFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: ProgramCyclesFiltersProps) => {
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
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <Grid container spacing={3} alignItems="flex-end">
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            fullWidth
            onChange={(e) => handleFilterChange('search', e.target.value)}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            variant="outlined"
            label={t('Status')}
            value={filter.status}
            fullWidth
          >
            {programCycleStatuses.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <NumberTextField
            id="totalEntitledQuantityUsdFromFilter"
            topLabel={t('Total Entitled Quantity')}
            value={filter.total_entitled_quantity_usd_from}
            placeholder={t('From')}
            onChange={(e) =>
              handleFilterChange(
                'total_entitled_quantity_usd_from',
                e.target.value,
              )
            }
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <NumberTextField
            id="totalEntitledQuantityUsdToFilter"
            value={filter.total_entitled_quantity_usd_to}
            placeholder={t('To')}
            onChange={(e) =>
              handleFilterChange(
                'total_entitled_quantity_usd_to',
                e.target.value,
              )
            }
            error={
              filter.total_entitled_quantity_usd_from &&
              filter.total_entitled_quantity_usd_to &&
              filter.total_entitled_quantity_usd_from >
                filter.total_entitled_quantity_usd_to
            }
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            topLabel="Date"
            onChange={(date) =>
              handleFilterChange(
                'start_date',
                date ? moment(date).format('YYYY-MM-DD') : '',
              )
            }
            value={filter.startDate}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            onChange={(date) =>
              handleFilterChange(
                'end_date',
                date ? moment(date).format('YYYY-MM-DD') : '',
              )
            }
            value={filter.end_date}
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
};
