import { Box, Grid, InputAdornment, MenuItem } from '@material-ui/core';
import FormControl from '@material-ui/core/FormControl';
import AssignmentIndRoundedIcon from '@material-ui/icons/AssignmentIndRounded';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import GroupIcon from '@material-ui/icons/Group';
import SearchIcon from '@material-ui/icons/Search';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import InputLabel from '../../shared/InputLabel';
import Select from '../../shared/Select';
import TextField from '../../shared/TextField';
import {
  HouseholdChoiceDataQuery,
  ProgramNode,
} from '../../__generated__/graphql';
import { ContainerWithBorder } from '../ContainerWithBorder';
import { FieldLabel } from '../FieldLabel';
import { AdminAreasAutocomplete } from './AdminAreaAutocomplete';

const TextContainer = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
`;
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

interface HouseholdFiltersProps {
  onFilterChange;
  filter;
  programs: ProgramNode[];
  choicesData: HouseholdChoiceDataQuery;
}
export function HouseholdFilters({
  onFilterChange,
  filter,
  programs,
  choicesData,
}: HouseholdFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
            variant='outlined'
            value={filter.text || ''}
            margin='dense'
            onChange={(e) => handleFilterChange(e, 'text')}
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
            <InputLabel>{t('Programme')}</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'program')}
              variant='outlined'
              label={t('Programme')}
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
                <em>{t('None')}</em>
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
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>{t('Residence Status')}</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'residenceStatus')}
              variant='outlined'
              label='Residence Status'
              value={filter.residenceStatus || ''}
              InputProps={{
                startAdornment: (
                  <StartInputAdornment position='start'>
                    <AssignmentIndRoundedIcon />
                  </StartInputAdornment>
                ),
              }}
              SelectDisplayProps={{
                'data-cy': 'filters-residence-status',
              }}
              MenuProps={{
                'data-cy': 'filters-residence-status-options',
              }}
            >
              {choicesData.residenceStatusChoices.map((program) => (
                <MenuItem key={program.value} value={program.value}>
                  {program.name}
                </MenuItem>
              ))}
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item>
          <AdminAreasAutocomplete
            onFilterChange={onFilterChange}
            name='adminArea'
          />
        </Grid>
        <Grid item>
          <Box display='flex' flexDirection='column'>
            <FieldLabel>{t('Household size')}</FieldLabel>
            <TextContainer
              id='minFilter'
              value={filter.householdSize.min}
              variant='outlined'
              margin='dense'
              placeholder={t('From')}
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  householdSize: {
                    ...filter.householdSize,
                    min: e.target.value || undefined,
                  },
                })
              }
              type='number'
              InputProps={{
                startAdornment: (
                  <InputAdornment position='start'>
                    <GroupIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Box>
        </Grid>
        <Grid item>
          <TextContainer
            id='maxFilter'
            value={filter.householdSize.max}
            variant='outlined'
            margin='dense'
            placeholder={t('To')}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                householdSize: {
                  ...filter.householdSize,
                  max: e.target.value || undefined,
                },
              })
            }
            type='number'
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <GroupIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
