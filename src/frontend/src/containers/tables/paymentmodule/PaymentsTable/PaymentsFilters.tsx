import { Grid, MenuItem } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiltersSection } from '@components/core/FiltersSection';
import { SearchTextField } from '@components/core/SearchTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import { createHandleApplyFilterChange } from '@utils/utils';
import type { ReactElement } from 'react';
import { useProgramContext } from 'src/programContext';
import { PaymentStatusEnum } from '@restgenerated/models/PaymentStatusEnum';

export interface PaymentFilterKeys {
  paymentUnicefId: string;
  individualUnicefId: string;
  householdUnicefId: string;
  collectorFullName: string;
  status?: string;
  ineligibilityCause?: string;
}

interface PaymentsFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  filterKeys: PaymentFilterKeys;
  showStatus?: boolean;
  showIneligibilityCause?: boolean;
}

export function PaymentsFilters({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  filterKeys,
  showStatus = false,
  showIneligibilityCause = false,
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
      <Grid
        container
        spacing={3}
        sx={{
          alignItems: 'flex-end',
        }}
      >
        <Grid size={3}>
          <SearchTextField
            label={t('Payment ID')}
            value={filter[filterKeys.paymentUnicefId]}
            fullWidth
            onChange={(e) =>
              handleFilterChange(filterKeys.paymentUnicefId, e.target.value)
            }
            data-cy="filter-payment-unicef-id"
          />
        </Grid>
        <Grid size={3}>
          {isSocialDctType ? (
            <SearchTextField
              label={t(`${beneficiaryGroup?.memberLabel} ID`)}
              value={filter[filterKeys.individualUnicefId]}
              fullWidth
              onChange={(e) =>
                handleFilterChange(
                  filterKeys.individualUnicefId,
                  e.target.value,
                )
              }
              data-cy="filter-individual-id"
            />
          ) : (
            <SearchTextField
              label={t(`${beneficiaryGroup?.groupLabel} ID`)}
              value={filter[filterKeys.householdUnicefId]}
              fullWidth
              onChange={(e) =>
                handleFilterChange(filterKeys.householdUnicefId, e.target.value)
              }
              data-cy="filter-household-id"
            />
          )}
        </Grid>
        <Grid size={3}>
          <SearchTextField
            label={t('Collector Full Name')}
            value={filter[filterKeys.collectorFullName]}
            fullWidth
            onChange={(e) =>
              handleFilterChange(filterKeys.collectorFullName, e.target.value)
            }
            data-cy="filter-collector-fullname"
          />
        </Grid>
        {showStatus && filterKeys.status && (
          <Grid size={3}>
            <SelectFilter
              label={t('Status')}
              value={filter[filterKeys.status]}
              onChange={(e) =>
                handleFilterChange(filterKeys.status, e.target.value)
              }
              dataCy="filter-payment-status"
            >
              {Object.values(PaymentStatusEnum)
                .filter(
                  (status) =>
                    status !== PaymentStatusEnum.NOT_ELIGIBLE &&
                    status !== PaymentStatusEnum.TRANSACTION_SUCCESSFUL,
                )
                .map((status) => (
                  <MenuItem key={status} value={status}>
                    {t(status)}
                  </MenuItem>
                ))}
            </SelectFilter>
          </Grid>
        )}
        {showIneligibilityCause && filterKeys.ineligibilityCause && (
          <Grid size={3}>
            <SelectFilter
              label={t('Ineligibility Cause')}
              value={filter[filterKeys.ineligibilityCause]}
              onChange={(e) =>
                handleFilterChange(
                  filterKeys.ineligibilityCause,
                  e.target.value,
                )
              }
              multiple
              dataCy="filter-ineligibility-cause"
            >
              <MenuItem value="conflicted">{t('Hard Conflict')}</MenuItem>
              <MenuItem value="excluded">{t('Manual Exclusion')}</MenuItem>
              <MenuItem value="invalid_wallet">{t('Invalid Wallet')}</MenuItem>
            </SelectFilter>
          </Grid>
        )}
      </Grid>
    </FiltersSection>
  );
}
