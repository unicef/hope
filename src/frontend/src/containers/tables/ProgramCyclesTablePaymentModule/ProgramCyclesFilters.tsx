import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { createHandleApplyFilterChange, formatFigure } from '@utils/utils';
import { MenuItem } from '@mui/material';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { NumberTextField } from '@core/NumberTextField';
import { DatePickerFilter } from '@core/DatePickerFilter';
import moment from 'moment/moment';
import { FiltersSection } from '@components/core/FiltersSection';
import type { ProgramChoices } from '@restgenerated/models/ProgramChoices';

interface ProgramCyclesFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  choicesData?: ProgramChoices;
}

export const ProgramCyclesFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  choicesData,
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
      <ResponsiveGridContainer
        spacing={3}
        sx={{
          alignItems: 'flex-end',
        }}
      >
        <ResponsiveGrid size="quarter">
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            fullWidth
            onChange={(e) => handleFilterChange('search', e.target.value)}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            variant="outlined"
            label={t('Status')}
            value={filter.status}
            fullWidth
          >
            {choicesData?.programCycleStatusChoices?.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <NumberTextField
            id="totalEntitledQuantityUsdFromFilter"
            topLabel={t('Total Entitled Quantity')}
            value={formatFigure(filter.totalEntitledQuantityUsdFrom)}
            placeholder={t('From')}
            onChange={(e) =>
              handleFilterChange('totalEntitledQuantityUsdFrom', e.target.value)
            }
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <NumberTextField
            id="totalEntitledQuantityUsdToFilter"
            value={formatFigure(filter.totalEntitledQuantityUsdTo)}
            placeholder={t('To')}
            onChange={(e) =>
              handleFilterChange('totalEntitledQuantityUsdTo', e.target.value)
            }
            error={
              filter.totalEntitledQuantityUsdFrom &&
              filter.totalEntitledQuantityUsdTo &&
              filter.totalEntitledQuantityUsdFrom >
                filter.totalEntitledQuantityUsdTo
            }
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <DatePickerFilter
            topLabel="Date"
            onChange={(date) =>
              handleFilterChange(
                'startDate',
                date ? moment(date).format('YYYY-MM-DD') : '',
              )
            }
            value={filter.startDate}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <DatePickerFilter
            onChange={(date) =>
              handleFilterChange(
                'endDate',
                date ? moment(date).format('YYYY-MM-DD') : '',
              )
            }
            value={filter.endDate}
          />
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </FiltersSection>
  );
};
