import React from 'react';
import styled from 'styled-components';
import SearchIcon from '@material-ui/icons/Search';
import CakeIcon from '@material-ui/icons/Cake';
import WcIcon from '@material-ui/icons/Wc';
import { TextField, InputAdornment, Select, MenuItem } from '@material-ui/core';
import { clearValue } from '../../utils/utils';

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
  .MuiFilledInput-input[value='none'] {
    color: red;
  }
  .MuiInputAdornment-filled.MuiInputAdornment-positionStart:not(.MuiInputAdornment-hiddenLabel) {
    margin: 0px;
  }
`;

interface IndividualsFilterProps {
  onFilterChange;
  filter;
}
export function IndividualsFilter({
  onFilterChange,
  filter,
}: IndividualsFilterProps): React.ReactElement {
  const handleFilterChange = (e, name) =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <Container>
      <TextContainer
        placeholder='Search'
        variant='filled'
        value={filter.text}
        onChange={(e) => handleFilterChange(e, 'text')}
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
        defaultValue={filter.sex}
        variant='filled'
        onChange={(e) => handleFilterChange(e, 'sex')}
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <WcIcon />
            </InputAdornment>
          ),
        }}
      >
        <MenuItem value='none'>Sex</MenuItem>
        <MenuItem value='MALE'>Male</MenuItem>
        <MenuItem value='FEMALE'>Female</MenuItem>
        <MenuItem value='OTHER'>Other</MenuItem>
      </TextContainer>
      <TextContainer
        variant='filled'
        placeholder='Age'
        value={filter.age.min}
        onChange={(e) =>
          onFilterChange({
            ...filter,
            age: { ...filter.age, min: e.target.value || undefined },
          })
        }
        type='number'
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <CakeIcon />
            </InputAdornment>
          ),
        }}
      />
      to
      <TextContainer
        variant='filled'
        placeholder='Age'
        value={filter.age.max}
        onChange={(e) =>
          onFilterChange({
            ...filter,
            age: { ...filter.age, max: e.target.value || undefined },
          })
        }
        type='number'
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <CakeIcon />
            </InputAdornment>
          ),
        }}
      />
    </Container>
  );
}
