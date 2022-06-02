import {
  Box,
  Button,
  Grid,
  InputAdornment,
  MenuItem,
  TextField,
} from '@material-ui/core';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import GroupIcon from '@material-ui/icons/Group';
import { KeyboardDatePicker } from '@material-ui/pickers';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  HouseholdChoiceDataQuery,
  ProgramNode,
} from '../../../../__generated__/graphql';
import { ContainerWithBorder } from '../../../core/ContainerWithBorder';
import { FieldLabel } from '../../../core/FieldLabel';
import { SearchTextField } from '../../../core/SearchTextField';
import { SelectFilter } from '../../../core/SelectFilter';
import { AdminAreaAutocomplete } from '../../../population/AdminAreaAutocomplete';

const TextContainer = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
`;

interface LookUpHouseholdFiltersProps {
  onFilterChange;
  filter;
  programs: ProgramNode[];
  choicesData: HouseholdChoiceDataQuery;
  setFilterHouseholdApplied?;
  householdFilterInitial?;
}
export function LookUpHouseholdFilters({
  onFilterChange,
  filter,
  programs,
  choicesData,
  setFilterHouseholdApplied,
  householdFilterInitial,
}: LookUpHouseholdFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange(e, 'search')}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'programs')}
            label={t('Programme')}
            value={filter.programs || []}
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
          <Box display='flex' flexDirection='column'>
            <FieldLabel>{t('Registration Date')}</FieldLabel>
            <KeyboardDatePicker
              variant='inline'
              inputVariant='outlined'
              margin='dense'
              placeholder={t('From')}
              autoOk
              onChange={(date) =>
                onFilterChange({
                  ...filter,
                  lastRegistrationDate: {
                    ...filter.lastRegistrationDate,
                    min: date ? moment(date).format('YYYY-MM-DD') : null,
                  },
                })
              }
              value={filter.lastRegistrationDate.min || null}
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
            placeholder={t('To')}
            autoOk
            onChange={(date) =>
              onFilterChange({
                ...filter,
                lastRegistrationDate: {
                  ...filter.lastRegistrationDate,
                  max: date ? moment(date).format('YYYY-MM-DD') : null,
                },
              })
            }
            value={filter.lastRegistrationDate.max || null}
            format='YYYY-MM-DD'
            InputAdornmentProps={{ position: 'end' }}
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'residenceStatus')}
            label={t('Status')}
            value={filter.residenceStatus || ''}
          >
            {choicesData.residenceStatusChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item>
          <AdminAreaAutocomplete
            onFilterChange={onFilterChange}
            name='admin2'
            value={filter.admin2}
          />
        </Grid>
        <Grid item>
          <Box display='flex' flexDirection='column'>
            <FieldLabel>{t('Household Size')}</FieldLabel>
            <TextContainer
              id='minFilter'
              value={filter.size.min || ''}
              variant='outlined'
              margin='dense'
              placeholder='From'
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  size: {
                    ...filter.size,
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
          <Box display='flex' flexDirection='column'>
            <FieldLabel>{t('Household Size')}</FieldLabel>
            <TextContainer
              id='maxFilter'
              value={filter.size.max || ''}
              variant='outlined'
              margin='dense'
              placeholder='To'
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  size: {
                    ...filter.size,
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
          </Box>
        </Grid>
        <Grid container justify='flex-end'>
          <Button
            color='primary'
            onClick={() => {
              setFilterHouseholdApplied(householdFilterInitial);
              onFilterChange(householdFilterInitial);
            }}
          >
            {t('Clear')}
          </Button>
          <Button
            color='primary'
            variant='outlined'
            onClick={() => setFilterHouseholdApplied(filter)}
          >
            {t('Apply')}
          </Button>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
