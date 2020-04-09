import React from 'react';
import styled from 'styled-components';
import { TextField, InputAdornment, Select, MenuItem } from '@material-ui/core';
import { Person, Search, Group } from '@material-ui/icons';

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
  const handleFilterChange = (e, name) =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <Container>
      <TextContainer
        placeholder='Search'
        variant='filled'
        onChange={(e) => handleFilterChange(e, 'name')}
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <Search />
            </InputAdornment>
          ),
        }}
      />
      <TextContainer
        select
        placeholder='Status'
        variant='filled'
        onChange={(e) => handleFilterChange(e, 'status')}
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <Person />
            </InputAdornment>
          ),
        }}
      >
        <MenuItem value=''>None</MenuItem>
        <MenuItem value='DRAFT'>Draft</MenuItem>
        <MenuItem value='APPROVED'>Approved</MenuItem>
        <MenuItem value='FINALIZED'>Finalized</MenuItem>
      </TextContainer>
      <TextContainer
        id='minFilter'
        value={filter.numIndividuals.min}
        variant='filled'
        placeholder='No. of Individuals'
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
        variant='filled'
        placeholder='No. of Individuals'
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
