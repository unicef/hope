import { Checkbox, FormControlLabel, Grid, MenuItem } from '@mui/material';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ContainerWithBorder } from '../../../components/core/ContainerWithBorder';
import { DatePickerFilter } from '../../../components/core/DatePickerFilter';
import { SelectFilter } from '../../../components/core/SelectFilter';

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
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });

  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SelectFilter
            label={t('Report Type')}
            onChange={(e) => handleFilterChange(e, 'type')}
            value={filter.type || ''}
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
            label={t('From')}
            onChange={(date) =>
              onFilterChange({
                ...filter,
                createdFrom: date
                  ? moment(date).startOf('day').toISOString()
                  : null,
              })
            }
            value={filter.createdFrom}
          />
        </Grid>
        <Grid item>
          <DatePickerFilter
            label={t('To')}
            onChange={(date) =>
              onFilterChange({
                ...filter,
                createdTo: date
                  ? moment(date).endOf('day').toISOString()
                  : null,
              })
            }
            value={filter.createdTo}
          />
        </Grid>
        <Grid item>
          <SelectFilter
            label='Status'
            onChange={(e) => handleFilterChange(e, 'status')}
            value={filter.status || ''}
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
                onChange={(e, checked) =>
                  onFilterChange({
                    ...filter,
                    onlyMy: checked,
                  })
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
