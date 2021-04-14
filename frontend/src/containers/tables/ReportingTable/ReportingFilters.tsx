import React from 'react';
import styled from 'styled-components';
import moment from 'moment';
import {
  Box,
  Checkbox,
  FormControl,
  FormControlLabel,
  Grid,
  InputLabel,
  MenuItem,
  Select,
} from '@material-ui/core';
import { KeyboardDatePicker } from '@material-ui/pickers';
import { ContainerWithBorder } from '../../../components/ContainerWithBorder';
import { FieldLabel } from '../../../components/FieldLabel';

const StyledFormControl = styled(FormControl)`
  width: 232px;
  color: #5f6368;
  border-bottom: 0;
`;
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
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Report Type</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'type')}
              variant='outlined'
              label='Type'
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
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item>
          <Box display='flex' flexDirection='column'>
            <FieldLabel>Creation Date</FieldLabel>
            <KeyboardDatePicker
              variant='inline'
              disableToolbar
              inputVariant='outlined'
              margin='dense'
              label='From'
              autoOk
              onChange={(date) =>
                onFilterChange({
                  ...filter,
                  createdFrom: date ? moment(date).startOf('day').toISOString() : null,
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
            disableToolbar
            inputVariant='outlined'
            margin='dense'
            label='To'
            autoOk
            onChange={(date) =>
              onFilterChange({
                ...filter,
                createdTo: date ? moment(date).endOf('day').toISOString() : null,
              })
            }
            value={filter.createdTo || null}
            format='YYYY-MM-DD'
            InputAdornmentProps={{ position: 'end' }}
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Status</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'status')}
              variant='outlined'
              label='Status'
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
            </Select>
          </StyledFormControl>
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
