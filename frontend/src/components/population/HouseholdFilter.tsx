import { Box, Grid, InputAdornment, MenuItem } from '@material-ui/core';
import AssignmentIndRoundedIcon from '@material-ui/icons/AssignmentIndRounded';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import GroupIcon from '@material-ui/icons/Group';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import TextField from '../../shared/TextField';
import {
  HouseholdChoiceDataQuery,
  ProgramNode,
} from '../../__generated__/graphql';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { FieldLabel } from '../core/FieldLabel';
import { SearchTextField } from '../core/SearchTextField';
import { SelectFilter } from '../core/SelectFilter';
import { AdminAreaAutocomplete } from './AdminAreaAutocomplete';

const TextContainer = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
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
            value={filter.text || ''}
            onChange={(e) => handleFilterChange(e, 'text')}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'program')}
            label={t('Programme')}
            value={filter.program || ''}
            icon={<FlashOnIcon />}
          >
            <MenuItem value=''>
              <em>{t('None')}</em>
            </MenuItem>
            {programs.map((program) => (
              <MenuItem key={program.id} value={program.id}>
                {program.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'residenceStatus')}
            label={t('Residence Status')}
            value={filter.residenceStatus || ''}
            icon={<AssignmentIndRoundedIcon />}
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
          </SelectFilter>
        </Grid>
        <Grid item>
          <AdminAreaAutocomplete
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
