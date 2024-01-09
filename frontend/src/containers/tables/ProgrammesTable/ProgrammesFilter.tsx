import { Grid, MenuItem } from '@material-ui/core';
import GroupIcon from '@material-ui/icons/Group';
import moment from 'moment';
import React from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { ProgrammeChoiceDataQuery } from '../../../__generated__/graphql';
import { DatePickerFilter } from '../../../components/core/DatePickerFilter';
import { FiltersSection } from '../../../components/core/FiltersSection';
import { NumberTextField } from '../../../components/core/NumberTextField';
import { SearchTextField } from '../../../components/core/SearchTextField';
import { SelectFilter } from '../../../components/core/SelectFilter';
import { createHandleApplyFilterChange } from '../../../utils/utils';

interface ProgrammesFilterProps {
  filter;
  choicesData: ProgrammeChoiceDataQuery;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const ProgrammesFilters = ({
  filter,
  choicesData,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: ProgrammesFilterProps): React.ReactElement => {
  const history = useHistory();
  const location = useLocation();

  const {
    handleFilterChange,
    applyFilterChanges,
    clearFilter,
  } = createHandleApplyFilterChange(
    initialFilter,
    history,
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
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            label='Search'
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            label='Status'
            value={filter.status}
            data-cy='filters-status'
          >
            {choicesData.programStatusChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            label='Start Date'
            data-cy='filters-start-date'
            onChange={(date) =>
              handleFilterChange(
                'startDate',
                date ? moment(date).format('YYYY-MM-DD') : '',
              )
            }
            value={filter.startDate}
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            label='End Date'
            data-cy='filters-end-date'
            onChange={(date) =>
              handleFilterChange(
                'endDate',
                date ? moment(date).format('YYYY-MM-DD') : '',
              )
            }
            value={filter.endDate}
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('sector', e.target.value)}
            label='Sector'
            data-cy='filters-sector'
            value={filter.sector}
            multiple
          >
            {choicesData.programSectorChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            data-cy='filters-number-of-households-min'
            topLabel='Num. of Households'
            placeholder='From'
            value={filter.numberOfHouseholdsMin}
            onChange={(e) =>
              handleFilterChange('numberOfHouseholdsMin', e.target.value)
            }
            icon={<GroupIcon />}
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            data-cy='filters-number-of-households-max'
            value={filter.numberOfHouseholdsMax}
            placeholder='To'
            onChange={(e) =>
              handleFilterChange('numberOfHouseholdsMax', e.target.value)
            }
            icon={<GroupIcon />}
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            data-cy='filters-budget-min'
            topLabel='Budget (USD)'
            value={filter.budgetMin}
            placeholder='From'
            onChange={(e) => handleFilterChange('budgetMin', e.target.value)}
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            data-cy='filters-budget-max'
            value={filter.budgetMax}
            placeholder='To'
            onChange={(e) => handleFilterChange('budgetMax', e.target.value)}
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('dataCollectingType', e.target.value)}
            label='Data Collecting Type'
            value={filter.dataCollectingType}
            data-cy='filters-data-collecting-type'
          >
            {choicesData.dataCollectionTypeChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
      </Grid>
    </FiltersSection>
  );
};
