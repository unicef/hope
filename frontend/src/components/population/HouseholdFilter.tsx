import React from 'react';
import styled from 'styled-components';
import { TextField, InputAdornment, MenuItem } from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import GroupIcon from '@material-ui/icons/Group';
import { ProgramNode } from '../../__generated__/graphql';
import FlashOnIcon from '@material-ui/icons/FlashOn';

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
  programs: ProgramNode[];
  minValue: number;
  maxValue: number;
  householdProgramFilter: (value: string) => void;
  householdMinSizeFilter: (value: number) => void;
  householdMaxSizeFilter: (value: number) => void;
  householdTextFilter: (value: string) => void;
}
export function HouseholdFilters({
  programs,
  minValue,
  maxValue,
  householdProgramFilter,
  householdMinSizeFilter,
  householdMaxSizeFilter,
  householdTextFilter,
}: HouseholdFiltersProps): React.ReactElement {
  return (
    <Container>
      <TextContainer
        placeholder='Search'
        variant='filled'
        onChange={(e) => householdTextFilter(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />
      <TextContainer
        select
        placeholder='Programme'
        variant='filled'
        onChange={(e) => householdProgramFilter(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <FlashOnIcon />
            </InputAdornment>
          ),
        }}
      >
        {programs.map((program) => (
          <MenuItem value={program.id}>{program.name}</MenuItem>
        ))}
      </TextContainer>
      <TextContainer
        id='minFilter'
        value={minValue}
        variant='filled'
        placeholder='Household size'
        onChange={(e) => householdMinSizeFilter(e.target.value)}
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
        value={maxValue}
        variant='filled'
        placeholder='Household size'
        onChange={(e) => householdMaxSizeFilter(e.target.value)}
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
