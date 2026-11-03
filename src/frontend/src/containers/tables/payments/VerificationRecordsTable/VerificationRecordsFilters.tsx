import { MenuItem } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiltersSection } from '@components/core/FiltersSection';
import { SearchTextField } from '@components/core/SearchTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import { createHandleApplyFilterChange } from '@utils/utils';
import type { ReactElement } from 'react';
import { useApiErrorSnackbar } from '@hooks/useApiErrorSnackbar';
import { useVerificationChannelChoices } from '@hooks/useVerificationChannelChoices';
import { useVerificationStatusChoices } from '@hooks/useVerificationStatusChoices';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

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
  const {
    data: verificationStatusChoices = [],
    isError: isStatusChoicesError,
    error: statusChoicesError,
  } = useVerificationStatusChoices();
  const {
    data: verificationChannelChoices = [],
    isError: isChannelChoicesError,
    error: channelChoicesError,
  } = useVerificationChannelChoices();

  // A failed lookup must not hide the filter bar — surface it and keep filtering usable.
  useApiErrorSnackbar(isStatusChoicesError, statusChoicesError);
  useApiErrorSnackbar(isChannelChoicesError, channelChoicesError);

  const verificationPlanOptions = verifications.map((item) => (
    <MenuItem key={item.unicefId} value={item.id}>
      {item.unicefId}
    </MenuItem>
  ));

  return (
    <FiltersSection
      applyHandler={handleApplyFilter}
      clearHandler={handleClearFilter}
    >
      <ResponsiveGridContainer spacing={3}>
        <ResponsiveGrid size="quarter">
          <SearchTextField
            value={filter.search}
            label={t('Search')}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filters-search"
            fullWidth
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('verificationStatus', e.target.value)
            }
            label={t('Verification Status')}
            value={filter.verificationStatus}
            fullWidth
          >
            {verificationStatusChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('verificationChannel', e.target.value)
            }
            label={t('Verification Channel')}
            value={filter.verificationChannel}
          >
            {verificationChannelChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('verificationPlanId', e.target.value)
            }
            label={t('Verification Plan Id')}
            value={filter.verificationPlanId}
          >
            {verificationPlanOptions}
          </SelectFilter>
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </FiltersSection>
  );
}
