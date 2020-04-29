import React from 'react';
import styled from 'styled-components';
import SearchIcon from '@material-ui/icons/Search';
import CakeIcon from '@material-ui/icons/Cake';
import WcIcon from '@material-ui/icons/Wc';
import { InputAdornment, MenuItem } from '@material-ui/core';
import FormControl from '@material-ui/core/FormControl';
import InputLabel from '../../shared/InputLabel';
import TextField from '../../shared/TextField';
import Select from '../../shared/Select';

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

interface IndividualsFilterProps {
  onFilterChange;
  filter;
}
export function IndividualsFilter({
  onFilterChange,
  filter,
}: IndividualsFilterProps): React.ReactElement {
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <Container>
      <SearchTextField
        label='Search'
        variant='outlined'
        margin='dense'
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
      <StyledFormControl variant='outlined' margin='dense'>
        <InputLabel>Sex</InputLabel>
        <Select
          /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
          // @ts-ignore
          onChange={(e) => handleFilterChange(e, 'sex')}
          variant='outlined'
          value={filter.sex || ''}
          label='Sex'
          InputProps={{
            startAdornment: (
              <StartInputAdornment position='start'>
                <WcIcon />
              </StartInputAdornment>
            ),
          }}
        >
          <MenuItem value=''>
            <em>None</em>
          </MenuItem>
          <MenuItem value='MALE'>Male</MenuItem>
          <MenuItem value='FEMALE'>Female</MenuItem>
        </Select>
      </StyledFormControl>
      <TextContainer
        variant='outlined'
        margin='dense'
        label='Age'
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
        variant='outlined'
        margin='dense'
        label='Age'
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
