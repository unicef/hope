import { Checkbox, FormControlLabel, Grid, MenuItem } from '@material-ui/core';
import moment from 'moment';
import React from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ContainerWithBorder } from '../../../components/core/ContainerWithBorder';
import { DatePickerFilter } from '../../../components/core/DatePickerFilter';
import { SelectFilter } from '../../../components/core/SelectFilter';
import { createHandleFilterChange } from '../../../utils/utils';

interface ReportingFiltersProps {
  onFilterChange;
  filter;
  choicesData;
}

export const ReportingFilters = ({
  onFilterChange,
  filter,
  choicesData,
}: ReportingFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );

  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SelectFilter
            label={t('Report Type')}
            onChange={(e) => handleFilterChange('type', e.target.value)}
            value={filter.type}
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
            {choicesData.reportTypesChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item>
          <DatePickerFilter
            topLabel={t('Creation Date')}
            placeholder={t('From')}
            onChange={(date) =>
              handleFilterChange(
                'createdFrom',
                moment(date)
                  .startOf('day')
                  .toISOString(),
              )
            }
            value={filter.createdFrom}
          />
        </Grid>
        <Grid item>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) =>
              handleFilterChange(
                'createdTo',
                moment(date)
                  .endOf('day')
                  .toISOString(),
              )
            }
            value={filter.createdTo}
          />
        </Grid>
        <Grid item>
          <SelectFilter
            label='Status'
            onChange={(e) => handleFilterChange('status', e.target.value)}
            value={filter.status}
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
            {choicesData.reportStatusChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item xs={12}>
          <FormControlLabel
            control={
              <Checkbox
                checked={filter.onlyMy}
                onChange={(_e, checked) =>
                  handleFilterChange('onlyMy', checked)
                }
                value={filter.onlyMy}
                color='primary'
              />
            }
            label='See my reports only'
          />
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
};
