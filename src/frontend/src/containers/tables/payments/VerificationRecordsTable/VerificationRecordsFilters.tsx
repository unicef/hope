import { Grid2 as Grid, MenuItem } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { usePaymentVerificationChoicesQuery } from '@generated/graphql';
import { FiltersSection } from '@components/core/FiltersSection';
import { SearchTextField } from '@components/core/SearchTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import { createHandleApplyFilterChange } from '@utils/utils';
import { ReactElement } from 'react';

interface VerificationRecordsFiltersProps {
  filter;
  verifications;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export function VerificationRecordsFilters({
  filter,
  verifications,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: VerificationRecordsFiltersProps): ReactElement {
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
  const { data: choicesData } = usePaymentVerificationChoicesQuery();
  if (!choicesData) {
    return null;
  }

  const verificationPlanOptions = verifications.edges.map((item) => (
    <MenuItem key={item.node.unicefId} value={item.node.id}>
      {item.node.unicefId}
    </MenuItem>
  ));

  return (
    <FiltersSection
      applyHandler={handleApplyFilter}
      clearHandler={handleClearFilter}
    >
      <Grid container spacing={3}>
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            value={filter.search}
            label={t('Search')}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filters-search"
            fullWidth
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            label={t('Verification Status')}
            value={filter.status}
            fullWidth
          >
            {choicesData.paymentVerificationStatusChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('verificationChannel', e.target.value)
            }
            label={t('Verification Channel')}
            value={filter.verificationChannel}
          >
            {choicesData.cashPlanVerificationVerificationChannelChoices.map(
              (item) => (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              ),
            )}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('paymentVerificationPlan', e.target.value)
            }
            label={t('Verification Plan Id')}
            value={filter.paymentVerificationPlan}
          >
            {verificationPlanOptions}
          </SelectFilter>
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
