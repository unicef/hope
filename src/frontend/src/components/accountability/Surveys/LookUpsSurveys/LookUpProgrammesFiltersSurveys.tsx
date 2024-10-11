import { Grid, MenuItem } from '@mui/material';
import GroupIcon from '@mui/icons-material/Group';
import moment from 'moment';
import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ProgrammeChoiceDataQuery } from '@generated/graphql';
import { createHandleApplyFilterChange } from '@utils/utils';
import { DatePickerFilter } from '@core/DatePickerFilter';
import { FiltersSection } from '@core/FiltersSection';
import { NumberTextField } from '@core/NumberTextField';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';

interface LookUpProgrammesFiltersSurveysProps {
  filter;
  choicesData: ProgrammeChoiceDataQuery;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export function LookUpProgrammesFiltersSurveys({
  filter,
  choicesData,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: LookUpProgrammesFiltersSurveysProps): React.ReactElement {
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
      applyHandler={handleApplyFilter}
      clearHandler={handleClearFilter}
      isOnPaper={false}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            label="Search"
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filters-search"
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            label="Status"
            value={filter.status}
            data-cy="filters-status"
          >
            {choicesData.programStatusChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
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
        </Grid>
        <Grid item xs={3}>
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
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('sector', e.target.value)}
            label="Sector"
            data-cy="filters-sector"
            value={filter.sector}
            multiple
          >
            {choicesData.programSectorChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            topLabel="Num. of Households"
            placeholder="From"
            data-cy="filters-number-of-households-min"
            value={filter.numberOfHouseholdsMin}
            onChange={(e) =>
              handleFilterChange('numberOfHouseholdsMin', e.target.value)
            }
            icon={<GroupIcon />}
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            data-cy="filters-number-of-households-max"
            value={filter.numberOfHouseholdsMax}
            placeholder="To"
            onChange={(e) =>
              handleFilterChange('numberOfHouseholdsMax', e.target.value)
            }
            icon={<GroupIcon />}
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            topLabel="Budget (USD)"
            data-cy="filters-budget-min"
            value={filter.budgetMin}
            placeholder="From"
            onChange={(e) => handleFilterChange('budgetMin', e.target.value)}
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            value={filter.budgetMax}
            data-cy="filters-budget-max"
            placeholder="To"
            onChange={(e) => handleFilterChange('budgetMax', e.target.value)}
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('dataCollectingType', e.target.value)
            }
            label="Data Collecting Type"
            value={filter.dataCollectingType}
            data-cy="filters-data-collecting-type"
          >
            {choicesData.dataCollectingTypeChoices.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
      </Grid>
    </FiltersSection>
  );
}
