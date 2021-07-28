import {
  Box,
  FormControl,
  Grid,
  InputAdornment,
  MenuItem,
} from '@material-ui/core';
import { Group, Person, Search } from '@material-ui/icons';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import InputLabel from '../../shared/InputLabel';
import Select from '../../shared/Select';
import TextField from '../../shared/TextField';
import { TARGETING_STATES } from '../../utils/constants';
import { ProgramNode } from '../../__generated__/graphql';
import { ContainerWithBorder } from '../ContainerWithBorder';
import { FieldLabel } from '../FieldLabel';

const TextContainer = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
`;
const SearchTextField = styled(TextField)`
  flex: 1;
  && {
    min-width: 150px;
  }
`;

const StyledFormControl = styled(FormControl)`
  width: 232px;
  color: #5f6368;
  border-bottom: 0;
`;

const StartInputAdornment = styled(InputAdornment)`
  margin-right: 0;
`;

interface TargetPopulationFiltersProps {
  //targetPopulations: TargetPopulationNode[],
  onFilterChange;
  filter;
  programs: ProgramNode[];
}
export function TargetPopulationFilters({
  // targetPopulations,
  onFilterChange,
  filter,
  programs,
}: TargetPopulationFiltersProps): React.ReactElement {
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
            value={filter.name || ''}
            margin='dense'
            onChange={(e) => handleFilterChange(e, 'name')}
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <Search />
                </InputAdornment>
              ),
            }}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>{t('Status')}</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'status')}
              variant='outlined'
              label={t('Programme')}
              InputProps={{
                startAdornment: (
                  <StartInputAdornment position='start'>
                    <Person />
                  </StartInputAdornment>
                ),
              }}
            >
              <MenuItem value=''>{TARGETING_STATES.NONE}</MenuItem>
              <MenuItem value='DRAFT'>{TARGETING_STATES.DRAFT}</MenuItem>
              <MenuItem value='APPROVED'>{TARGETING_STATES.APPROVED}</MenuItem>
              <MenuItem value='FINALIZED'>
                {TARGETING_STATES.FINALIZED}
              </MenuItem>
            </Select>
          </StyledFormControl>
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
          <Box display='flex' flexDirection='column'>
            <FieldLabel>{t('Number of Households')}</FieldLabel>
            <TextContainer
              id='minFilter'
              value={filter.numIndividuals.min}
              variant='outlined'
              margin='dense'
              placeholder={t('From')}
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  numIndividuals: {
                    ...filter.numIndividuals,
                    min: e.target.value || undefined,
                  },
                })
              }
              type='number'
              InputProps={{
                startAdornment: (
                  <InputAdornment position='start'>
                    <Group />
                  </InputAdornment>
                ),
              }}
            />
          </Box>
        </Grid>
        <Grid item>
          <TextContainer
            id='maxFilter'
            value={filter.numIndividuals.max}
            variant='outlined'
            margin='dense'
            placeholder={t('To')}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                numIndividuals: {
                  ...filter.numIndividuals,
                  max: e.target.value || undefined,
                },
              })
            }
            type='number'
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <Group />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
