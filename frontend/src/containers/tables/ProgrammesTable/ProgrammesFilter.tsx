import { Grid, MenuItem } from '@material-ui/core';
import GroupIcon from '@material-ui/icons/Group';
import moment from 'moment';
import React from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { DatePickerFilter } from '../../../components/core/DatePickerFilter';
import { NumberTextField } from '../../../components/core/NumberTextField';
import { SearchTextField } from '../../../components/core/SearchTextField';
import { SelectFilter } from '../../../components/core/SelectFilter';
import { createHandleFilterChange } from '../../../utils/utils';
import { ProgrammeChoiceDataQuery } from '../../../__generated__/graphql';

interface ProgrammesFilterProps {
  onFilterChange;
  filter;
  choicesData: ProgrammeChoiceDataQuery;
}
export const ProgrammesFilters = ({
  onFilterChange,
  filter,
  choicesData,
}: ProgrammesFilterProps): React.ReactElement => {
  const history = useHistory();
  const location = useLocation();

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );

  return (
    <Grid container alignItems='center' spacing={3}>
      <Grid container alignItems='center' spacing={3}>
        <Grid item xs={12}>
          <Grid container alignItems='center' spacing={3}>
            <Grid item xs={6}>
              <SearchTextField
                label='Search'
                value={filter.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                data-cy='filters-search'
                fullWidth
              />
            </Grid>
            <Grid item xs={6}>
              <SelectFilter
                onChange={(e) => handleFilterChange('status', e.target.value)}
                label='Status'
                value={filter.status}
                fullWidth
              >
                <MenuItem value=''>
                  <em>None</em>
                </MenuItem>
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
                onChange={(date) =>
                  handleFilterChange(
                    'startDate',
                    moment(date).format('YYYY-MM-DD'),
                  )
                }
                value={filter.startDate}
              />
            </Grid>
            <Grid item xs={3}>
              <DatePickerFilter
                label='End Date'
                onChange={(date) =>
                  handleFilterChange(
                    'endDate',
                    moment(date).format('YYYY-MM-DD'),
                  )
                }
                value={filter.endDate}
              />
            </Grid>
            <Grid item xs={6}>
              <SelectFilter
                onChange={(e) => handleFilterChange('sector', e.target.value)}
                label='Sector'
                value={filter.sector}
                fullWidth
                multiple
              >
                <MenuItem value=''>
                  <em>None</em>
                </MenuItem>
                {choicesData.programSectorChoices.map((item) => {
                  return (
                    <MenuItem key={item.value} value={item.value}>
                      {item.name}
                    </MenuItem>
                  );
                })}
              </SelectFilter>
            </Grid>
          </Grid>
        </Grid>
        <Grid item xs={12}>
          <Grid container alignItems='flex-end' spacing={3}>
            <Grid item xs={3}>
              <NumberTextField
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
                topLabel='Budget (USD)'
                value={filter.budgetMin}
                placeholder='From'
                onChange={(e) =>
                  handleFilterChange('budgetMin', e.target.value)
                }
              />
            </Grid>
            <Grid item xs={3}>
              <NumberTextField
                value={filter.budgetMax}
                placeholder='To'
                onChange={(e) =>
                  handleFilterChange('budgetMax', e.target.value)
                }
              />
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
};
