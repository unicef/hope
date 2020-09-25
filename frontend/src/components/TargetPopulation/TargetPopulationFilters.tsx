import React from 'react';
import styled from 'styled-components';
import {
  TextField,
  InputAdornment,
  MenuItem,
  FormControl,
} from '@material-ui/core';
import { Person, Search, Group } from '@material-ui/icons';
import Select from '../../shared/Select';
import InputLabel from '../../shared/InputLabel';
import { TARGETING_STATES } from '../../utils/constants';

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
  .MuiFilledInput-root {
    border-radius: 4px;
  }
  && {
    width: 232px;
    color: #5f6368;
    border-bottom: 0;
  }
  .MuiFilledInput-underline:before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline:before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline:hover {
    border-bottom: 0;
    border-radius: 4px;
  }
  .MuiFilledInput-underline:hover::before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline::before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline::after {
    border-bottom: 0;
  }
  .MuiFilledInput-underline::after:hover {
    border-bottom: 0;
  }
  .MuiSvgIcon-root {
    color: #5f6368;
  }
  .MuiFilledInput-input {
    padding: 10px 15px 10px;
  }
  .MuiInputAdornment-filled.MuiInputAdornment-positionStart:not(.MuiInputAdornment-hiddenLabel) {
    margin: 0px;
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

interface HouseholdFiltersProps {
  //targetPopulations: TargetPopulationNode[],
  onFilterChange;
  filter;
}
export function TargetPopulationFilters({
  // targetPopulations,
  onFilterChange,
  filter,
}: HouseholdFiltersProps): React.ReactElement {
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <Container>
      <TextContainer
        placeholder='Search'
        variant='outlined'
        margin='dense'
        onChange={(e) => handleFilterChange(e, 'name')}
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <Search />
            </InputAdornment>
          ),
        }}
      />
      <StyledFormControl variant='outlined' margin='dense'>
        <InputLabel>Status</InputLabel>
        <Select
          /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
          // @ts-ignore
          onChange={(e) => handleFilterChange(e, 'status')}
          variant='outlined'
          label='Programme'
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
          <MenuItem value='FINALIZED'>{TARGETING_STATES.FINALIZED}</MenuItem>
        </Select>
      </StyledFormControl>
      <TextContainer
        id='minFilter'
        value={filter.numIndividuals.min}
        variant='outlined'
        margin='dense'
        placeholder='Number of Household'
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
      to
      <TextContainer
        id='maxFilter'
        value={filter.numIndividuals.max}
        variant='outlined'
        margin='dense'
        placeholder='Number of Household'
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
    </Container>
  );
}
