import {
  Box,
  Button,
  Grid,
  InputAdornment,
  MenuItem,
  TextField,
} from '@material-ui/core';
import FormControl from '@material-ui/core/FormControl';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import GroupIcon from '@material-ui/icons/Group';
import SearchIcon from '@material-ui/icons/Search';
import { KeyboardDatePicker } from '@material-ui/pickers';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import InputLabel from '../../../shared/InputLabel';
import Select from '../../../shared/Select';
import {
  HouseholdChoiceDataQuery,
  ProgramNode,
} from '../../../__generated__/graphql';
import { ContainerWithBorder } from '../../ContainerWithBorder';
import { FieldLabel } from '../../FieldLabel';
import { AdminAreasAutocomplete } from '../../population/AdminAreaAutocomplete';

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
            variant='outlined'
            margin='dense'
            value={filter.search}
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
            <InputLabel>{t('Programme')}</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'programs')}
              variant='outlined'
              label={t('Programme')}
              value={filter.programs || []}
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
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>{t('Status')}</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'residenceStatus')}
              variant='outlined'
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
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item>
          <AdminAreasAutocomplete
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
