import React from 'react';
import moment from 'moment';
import {
  Box,
  Checkbox,
  FormControlLabel,
  Grid,
  InputLabel,
  MenuItem,
  Select,
} from '@material-ui/core';
import { KeyboardDatePicker } from '@material-ui/pickers';
import { ContainerWithBorder } from '../../../components/core/ContainerWithBorder';
import { FieldLabel } from '../../../components/core/FieldLabel';
import { StyledFormControl } from '../../../components/StyledFormControl';
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
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });

  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SelectFilter
            label='Report Type'
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
          <Box display='flex' flexDirection='column'>
            <FieldLabel>Creation Date</FieldLabel>
            <KeyboardDatePicker
              variant='inline'
              inputVariant='outlined'
              margin='dense'
              label='From'
              autoOk
              onChange={(date) =>
                onFilterChange({
                  ...filter,
                  createdFrom: date
                    ? moment(date)
                        .startOf('day')
                        .toISOString()
                    : null,
                })
              }
              value={filter.createdFrom || null}
              format='YYYY-MM-DD'
              InputAdornmentProps={{ position: 'end' }}
            />
          </Box>
        </Grid>
        <Grid item>
          <KeyboardDatePicker
            variant='inline'
            inputVariant='outlined'
            margin='dense'
            label='To'
            autoOk
            onChange={(date) =>
              onFilterChange({
                ...filter,
                createdTo: date
                  ? moment(date)
                      .endOf('day')
                      .toISOString()
                  : null,
              })
            }
            value={filter.createdTo || null}
            format='YYYY-MM-DD'
            InputAdornmentProps={{ position: 'end' }}
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
