import { Grid } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiltersSection } from '@components/core/FiltersSection';
import { SearchTextField } from '@components/core/SearchTextField';
import { createHandleApplyFilterChange } from '@utils/utils';
import { ReactElement } from 'react';

interface PaymentsFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

export function PaymentsFilters({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: PaymentsFiltersProps): ReactElement {
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
        <Grid size={3}>
          <SearchTextField
            label={t('Payment ID')}
            value={filter.paymentUnicefId}
            fullWidth
            onChange={(e) =>
              handleFilterChange('paymentUnicefId', e.target.value)
            }
            data-cy="filter-payment-unicef-id"
          />
        </Grid>
        <Grid size={3}>
          <SearchTextField
            label={t('Household ID')}
            value={filter.householdUnicefId}
            fullWidth
            onChange={(e) =>
              handleFilterChange('householdUnicefId', e.target.value)
            }
            data-cy="filter-household-id"
          />
        </Grid>
        <Grid size={3}>
          <SearchTextField
            label={t('Collector Full Name')}
            value={filter.collectorFullname}
            fullWidth
            onChange={(e) =>
              handleFilterChange('collectorFullname', e.target.value)
            }
            data-cy="filter-collector-fullname"
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
