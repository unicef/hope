import { MenuItem } from '@mui/material';
import GroupIcon from '@mui/icons-material/Group';
import moment from 'moment';
import { useLocation, useNavigate } from 'react-router-dom';
import type { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import type { DataCollectingTypeChoice } from '@restgenerated/models/DataCollectingTypeChoice';
import { DatePickerFilter } from '@components/core/DatePickerFilter';
import { FiltersSection } from '@components/core/FiltersSection';
import { NumberTextField } from '@components/core/NumberTextField';
import { SearchTextField } from '@components/core/SearchTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import { createHandleApplyFilterChange } from '@utils/utils';
import type { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

interface ProgrammesFilterProps {
  filter;
  choicesData: ProgramChoices;
  dataCollectingTypeChoices: DataCollectingTypeChoice[];
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
function ProgrammesFilters({
  filter,
  choicesData,
  dataCollectingTypeChoices,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: ProgrammesFilterProps): ReactElement {
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
        <ResponsiveGrid size="sixth">
          <SearchTextField
            label="Search"
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filters-search"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="sixth">
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            label="Status"
            value={filter.status}
            data-cy="filters-status"
          >
            {choicesData.statusChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
        <ResponsiveGrid size="sixth">
          <DatePickerFilter
            label="Start Date"
            dataCy="filters-start-date"
            onChange={(date) =>
              handleFilterChange(
                'startDate',
                date ? moment(date).format('YYYY-MM-DD') : '',
              )
            }
            value={filter.startDate}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="sixth">
          <DatePickerFilter
            label="End Date"
            dataCy="filters-end-date"
            onChange={(date) =>
              handleFilterChange(
                'endDate',
                date ? moment(date).format('YYYY-MM-DD') : '',
              )
            }
            value={filter.endDate}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="third">
          <SelectFilter
            onChange={(e) => handleFilterChange('sector', e.target.value)}
            label="Sector"
            dataCy="filters-sector"
            value={filter.sector}
            multiple
          >
            {choicesData.sectorChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
        <ResponsiveGrid size="sixth" mobileSize="half">
          <NumberTextField
            data-cy="filters-number-of-households-min"
            topLabel="Programme Size"
            placeholder="From"
            value={filter.numberOfHouseholdsMin}
            onChange={(e) =>
              handleFilterChange('numberOfHouseholdsMin', e.target.value)
            }
            icon={<GroupIcon />}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="sixth" mobileSize="half">
          <NumberTextField
            data-cy="filters-number-of-households-max"
            value={filter.numberOfHouseholdsMax}
            placeholder="To"
            onChange={(e) =>
              handleFilterChange('numberOfHouseholdsMax', e.target.value)
            }
            icon={<GroupIcon />}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="sixth" mobileSize="half">
          <NumberTextField
            data-cy="filters-budget-min"
            topLabel="Budget (USD)"
            value={filter.budgetMin}
            placeholder="From"
            onChange={(e) => handleFilterChange('budgetMin', e.target.value)}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="sixth" mobileSize="half">
          <NumberTextField
            data-cy="filters-budget-max"
            value={filter.budgetMax}
            placeholder="To"
            onChange={(e) => handleFilterChange('budgetMax', e.target.value)}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('dataCollectingType', e.target.value)
            }
            label="Data Collecting Type"
            value={filter.dataCollectingType}
            data-cy="filters-data-collecting-type"
          >
            {dataCollectingTypeChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </FiltersSection>
  );
}

export default withErrorBoundary(ProgrammesFilters, 'ProgrammesFilters');
