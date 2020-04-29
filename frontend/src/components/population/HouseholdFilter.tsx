import React from 'react';
import styled from 'styled-components';
import { InputAdornment, MenuItem } from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import GroupIcon from '@material-ui/icons/Group';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import FormControl from '@material-ui/core/FormControl';
import AssignmentIndRoundedIcon from '@material-ui/icons/AssignmentIndRounded';
import {
  HouseholdChoiceDataQuery,
  ProgramNode,
} from '../../__generated__/graphql';
import TextField from '../../shared/TextField';
import InputLabel from '../../shared/InputLabel';
import Select from '../../shared/Select';
import { AdminAreasAutocomplete } from './AdminAreaAutocomplete';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: row;
  align-items: center;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;

  && > div {
    margin: 5px;
  }
`;

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
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <Container>
      <SearchTextField
        label='Search'
        variant='outlined'
        margin='dense'
        onChange={(e) => handleFilterChange(e, 'text')}
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />
      <StyledFormControl variant='outlined' margin='dense'>
        <InputLabel>Programme</InputLabel>
        <Select
          /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
          // @ts-ignore
          onChange={(e) => handleFilterChange(e, 'program')}
          variant='outlined'
          label='Programme'
          value={filter.program||""}
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
      <StyledFormControl variant='outlined' margin='dense'>
        <InputLabel>Residence Status</InputLabel>
        <Select
          /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
          // @ts-ignore
          onChange={(e) => handleFilterChange(e, 'residenceStatus')}
          variant='outlined'
          label='Residence Status'
          value={filter.residenceStatus||""}
          InputProps={{
            startAdornment: (
              <StartInputAdornment position='start'>
                <AssignmentIndRoundedIcon />
              </StartInputAdornment>
            ),
          }}
        >
          <MenuItem value=''>
            <em>None</em>
          </MenuItem>
          {choicesData.residenceStatusChoices.map((program) => (
            <MenuItem key={program.value} value={program.value}>{program.name}</MenuItem>
          ))}
        </Select>
      </StyledFormControl>
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
      <TextContainer
        id='minFilter'
        value={filter.householdSize.min}
        variant='outlined'
        margin='dense'
        label='Household size'
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
      to
      <TextContainer
        id='maxFilter'
        value={filter.householdSize.max}
        variant='outlined'
        margin='dense'
        label='Household size'
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
    </Container>
  );
}
