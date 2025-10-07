import { Grid, MenuItem } from '@mui/material';
import { Group, Person } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { createHandleApplyFilterChange } from '@utils/utils';
import { DatePickerFilter } from '@core/DatePickerFilter';
import { NumberTextField } from '@core/NumberTextField';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { FiltersSection } from '@core/FiltersSection';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';

interface TargetPopulationTableFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const TargetPopulationTableFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: TargetPopulationTableFiltersProps): ReactElement => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
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

  const allowedStatusChoices = [
    'ASSIGNED',
    PaymentPlanStatusEnum.DRAFT,
    PaymentPlanStatusEnum.TP_OPEN,
    PaymentPlanStatusEnum.TP_LOCKED,
    PaymentPlanStatusEnum.PROCESSING,
    PaymentPlanStatusEnum.STEFICON_RUN,
    PaymentPlanStatusEnum.STEFICON_WAIT,
    PaymentPlanStatusEnum.STEFICON_COMPLETED,
    PaymentPlanStatusEnum.STEFICON_ERROR,
  ];

  const { data: statusChoicesData } = useQuery({
    queryKey: ['choicesPaymentPlanStatusList'],
    queryFn: () => RestService.restChoicesPaymentPlanStatusList(),
  });

  const preparedStatusChoices =
    [
      { name: 'Assigned', value: 'ASSIGNED' },
      { name: 'Ready for Payment Module', value: PaymentPlanStatusEnum.DRAFT },
      ...(statusChoicesData || []),
    ]
      ?.filter((el) =>
        allowedStatusChoices.includes(el.value as PaymentPlanStatusEnum),
      )
      ?.filter((el) => el.name !== 'Draft') || [];

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid size={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.name}
            onChange={(e) => handleFilterChange('name', e.target.value)}
            data-cy="filters-search"
            fullWidth
          />
        </Grid>
        <Grid size={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            value={filter.status}
            label={t('Status')}
            icon={<Person />}
            fullWidth
            data-cy="filters-status"
          >
            {preparedStatusChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={3}>
          <NumberTextField
            topLabel={t(`Number of ${beneficiaryGroup?.groupLabelPlural}`)}
            value={filter.totalHouseholdsCountGte}
            placeholder={t('From')}
            onChange={(e) =>
              handleFilterChange('totalHouseholdsCountGte', e.target.value)
            }
            icon={<Group />}
            data-cy="filters-total-households-count-min"
          />
        </Grid>
        <Grid size={3}>
          <NumberTextField
            value={filter.totalHouseholdsCountLte}
            placeholder={t('To')}
            onChange={(e) =>
              handleFilterChange('totalHouseholdsCountLte', e.target.value)
            }
            icon={<Group />}
            data-cy="filters-total-households-count-max"
          />
        </Grid>
        <Grid size={3}>
          <DatePickerFilter
            topLabel={t('Date Created')}
            placeholder={t('From')}
            onChange={(date) => handleFilterChange('createdAtGte', date)}
            value={filter.createdAtGte}
          />
        </Grid>
        <Grid size={3}>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) => handleFilterChange('createdAtLte', date)}
            value={filter.createdAtLte}
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
};
