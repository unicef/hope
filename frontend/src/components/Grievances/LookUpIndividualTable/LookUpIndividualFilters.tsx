import React from 'react';
import styled from 'styled-components';
import moment from 'moment';
import SearchIcon from '@material-ui/icons/Search';
import CakeIcon from '@material-ui/icons/Cake';
import WcIcon from '@material-ui/icons/Wc';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import {
  Box,
  Grid,
  InputAdornment,
  MenuItem,
  TextField,
} from '@material-ui/core';
import FormControl from '@material-ui/core/FormControl';
import { ContainerWithBorder } from '../../ContainerWithBorder';
import InputLabel from '../../../shared/InputLabel';
import Select from '../../../shared/Select';
import { FieldLabel } from '../../FieldLabel';
import { KeyboardDatePicker } from '@material-ui/pickers';
import { HouseholdChoiceDataQuery } from '../../../__generated__/graphql';
import { AdminAreasAutocomplete } from '../../population/AdminAreaAutocomplete';

const StyledFormControl = styled(FormControl)`
  width: 232px;
  color: #5f6368;
  border-bottom: 0;
`;

const SearchTextField = styled(TextField)`
  flex: 1;
  && {
    min-width: 150px;
  }
`;
const StartInputAdornment = styled(InputAdornment)`
  margin-right: 0;
`;

interface LookUpIndividualFiltersProps {
  onFilterChange;
  filter;
  programs;
  choicesData: HouseholdChoiceDataQuery;
}
export function LookUpIndividualFilters({
  onFilterChange,
  filter,
  programs,
  choicesData,
}: LookUpIndividualFiltersProps): React.ReactElement {
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label='Search'
            variant='outlined'
            margin='dense'
            value={filter.text}
            onChange={(e) => handleFilterChange(e, 'search')}
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Programme</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'program')}
              variant='outlined'
              label='Programme'
              value={filter.program || ''}
              InputProps={{
                startAdornment: (
                  <StartInputAdornment position='start'>
                    <FlashOnIcon />
                  </StartInputAdornment>
                ),
              }}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {programs.map((program) => (
                <MenuItem key={program.id} value={program.id}>
                  {program.name}
                </MenuItem>
              ))}
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item>
          <Box display='flex' flexDirection='column'>
            <FieldLabel>Registration Date</FieldLabel>
            <KeyboardDatePicker
              variant='inline'
              disableToolbar
              inputVariant='outlined'
              margin='dense'
              placeholder='From'
              autoOk
              onChange={(date) =>
                onFilterChange({
                  ...filter,
                  startDate: date ? moment(date).format('YYYY-MM-DD') : null,
                })
              }
              value={filter.startDate || null}
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
            placeholder='To'
            autoOk
            onChange={(date) =>
              onFilterChange({
                ...filter,
                endDate: date ? moment(date).format('YYYY-MM-DD') : null,
              })
            }
            value={filter.endDate || null}
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
              value={filter.residenceStatus || null}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {choicesData.residenceStatusChoices.map((item) => {
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
          <AdminAreasAutocomplete
            value={filter.adminArea}
            onChange={(e, option) => {
              if (!option) {
                onFilterChange({ ...filter, adminArea: undefined });
                return;
              }
              onFilterChange({ ...filter, adminArea: option.node.id });
            }}
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Gender</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'sex')}
              variant='outlined'
              value={filter.sex || ''}
              label='Gender'
              InputProps={{
                startAdornment: (
                  <StartInputAdornment position='start'>
                    <WcIcon />
                  </StartInputAdornment>
                ),
              }}
              SelectDisplayProps={{
                'data-cy': 'filters-sex',
              }}
              MenuProps={{
                'data-cy': 'filters-sex-options',
              }}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              <MenuItem value='MALE'>Male</MenuItem>
              <MenuItem value='FEMALE'>Female</MenuItem>
            </Select>
          </StyledFormControl>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
