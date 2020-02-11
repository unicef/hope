import React from 'react';
import styled from 'styled-components';
import { MenuItem, Select, TextField, InputAdornment } from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import GroupIcon from '@material-ui/icons/Group';

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
  && {
    width: 232px;
    color: #5f6368;
    border-bottom: 0;
    border-radius: 4px;
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

const SelectContainer = styled(Select)`
  && {
    width: 232px;
    background-color: rgba(0, 0, 0, 0.08);
    color: #5f6368;
    border-bottom-width: 0;
    border-radius: 4px;
    height: 40px;
  }
  .MuiInput-underline:before {
    border-bottom: none;
  }
  .MuiInput-underline:after {
    border-bottom: none;
  }
  &&:hover {
    border-bottom-width: 0;
    border-radius: 4px;
  }
  &&:hover::before {
    border-bottom-width: 0;
  }
  &&::before {
    border-bottom-width: 0;
  }
  &&::after {
    border-bottom-width: 0;
  }
  &&::after:hover {
    border-bottom-width: 0;
  }
  .MuiSvgIcon-root {
    color: #5f6368;
  }
`;

export function HouseholdFilters(): React.ReactElement {
  return (
    <Container>
      <TextContainer
        placeholder='Search'
        variant='filled'
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />
      <SelectContainer variant='filled' placeholder='Household size'>
        <MenuItem value='' disabled>
          Placeholder
        </MenuItem>
      </SelectContainer>
      <TextContainer
        variant='filled'
        placeholder='Household size'
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
        variant='filled'
        placeholder='Household size'
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
