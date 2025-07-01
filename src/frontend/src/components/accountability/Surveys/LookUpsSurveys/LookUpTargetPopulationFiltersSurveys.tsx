import { Grid2 as Grid, MenuItem } from '@mui/material';
import { Group, Person } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import {
  createHandleApplyFilterChange,
  paymentPlanStatusMapping,
} from '@utils/utils';
import { DatePickerFilter } from '@core/DatePickerFilter';
import { FiltersSection } from '@core/FiltersSection';
import { NumberTextField } from '@core/NumberTextField';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface LookUpTargetPopulationFiltersSurveysProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
function LookUpTargetPopulationFiltersSurveys({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: LookUpTargetPopulationFiltersSurveysProps): ReactElement {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const isAccountability = location.pathname.includes('accountability');
  const { selectedProgram } = useProgramContext();
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

  const preparedStatusChoices = isAccountability
    ? Object.values(PaymentPlanStatusEnum).filter((key) => key !== 'OPEN')
    : Object.values(PaymentPlanStatusEnum);

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
      isOnPaper={false}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            label={t('Search')}
            value={filter.name}
            onChange={(e) => handleFilterChange('name', e.target.value)}
            data-cy="filters-search"
            fullWidth
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            value={filter.status}
            label={t('Status')}
            icon={<Person />}
            fullWidth
            data-cy="filters-status"
          >
            {preparedStatusChoices.sort().map((key) => (
              <MenuItem key={key} value={key}>
                {paymentPlanStatusMapping(key)}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <NumberTextField
            topLabel={t(`Number of ${beneficiaryGroup?.groupLabelPlural}`)}
            value={filter.totalHouseholdsCountMin}
            placeholder={t('From')}
            onChange={(e) =>
              handleFilterChange('totalHouseholdsCountMin', e.target.value)
            }
            icon={<Group />}
            data-cy="filters-total-households-count-min"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <NumberTextField
            value={filter.totalHouseholdsCountMax}
            placeholder={t('To')}
            onChange={(e) =>
              handleFilterChange('totalHouseholdsCountMax', e.target.value)
            }
            icon={<Group />}
            data-cy="filters-total-households-count-max"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            topLabel={t('Date Created')}
            placeholder={t('From')}
            onChange={(date) => handleFilterChange('createdAtRangeMin', date)}
            value={filter.createdAtRangeMin}
            dataCy="filters-creation-date-from"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) => handleFilterChange('createdAtRangeMax', date)}
            value={filter.createdAtRangeMax}
            dataCy="filters-creation-date-to"
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
}

export default withErrorBoundary(
  LookUpTargetPopulationFiltersSurveys,
  'LookUpTargetPopulationFiltersSurveys',
);
