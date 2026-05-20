import { Grid } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiltersSection } from '@components/core/FiltersSection';
import { SearchTextField } from '@components/core/SearchTextField';
import { createHandleApplyFilterChange } from '@utils/utils';
import { ReactElement } from 'react';
import { useProgramContext } from 'src/programContext';

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
  const { isSocialDctType, selectedProgram } = useProgramContext();
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
          {isSocialDctType ? (
            <SearchTextField
              label={t(`${beneficiaryGroup?.memberLabel} ID`)}
              value={filter.individualUnicefId}
              fullWidth
              onChange={(e) =>
                handleFilterChange('individualUnicefId', e.target.value)
              }
              data-cy="filter-individual-id"
            />
          ) : (
            <SearchTextField
              label={t(`${beneficiaryGroup?.groupLabel} ID`)}
              value={filter.householdUnicefId}
              fullWidth
              onChange={(e) =>
                handleFilterChange('householdUnicefId', e.target.value)
              }
              data-cy="filter-household-id"
            />
          )}
        </Grid>
        <Grid size={3}>
          <SearchTextField
            label={t('Collector Full Name')}
            value={filter.collectorFullName}
            fullWidth
            onChange={(e) =>
              handleFilterChange('collectorFullName', e.target.value)
            }
            data-cy="filter-collector-fullname"
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
