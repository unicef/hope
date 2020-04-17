import React from 'react';
import styled from 'styled-components';
import { InputAdornment, MenuItem } from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import FormControl from '@material-ui/core/FormControl';
import { KeyboardDatePicker } from '@material-ui/pickers';
import { useRegistrationChoicesQuery } from '../../../__generated__/graphql';
import InputLabel from '../../../shared/InputLabel';
import TextField from '../../../shared/TextField';
import Select from '../../../shared/Select';
import { UsersAutocomplete } from './UsersAutocomplete';

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

const StyledFormControl = styled(FormControl)`
  width: 232px;
  color: #5f6368;
  border-bottom: 0;
`;

const StyledTextField = styled(TextField)`
  flex: 1;
  && {
    min-width: 150px;
  }
`;

interface RegistrationFiltersProps {
  onFilterChange;
  filter;
}
export function RegistrationFilters({
  onFilterChange,
  filter,
}: RegistrationFiltersProps): React.ReactElement {
  const handleFilterChange = (e, name) =>
    onFilterChange({ ...filter, [name]: e.target.value });
  const { data: registrationChoicesData } = useRegistrationChoicesQuery();
  if (!registrationChoicesData) {
    return null;
  }

  return (
    <Container>
      <StyledTextField
        variant='outlined'
        label='Search'
        margin='dense'
        onChange={(e) => handleFilterChange(e, 'search')}
        value={filter.search}
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />
      <KeyboardDatePicker
        variant='inline'
        disableToolbar
        inputVariant='outlined'
        margin='dense'
        label='Import Date'
        autoOk
        onChange={(date) => onFilterChange({ ...filter, importDate: date })}
        value={filter.importDate || null}
        format='DD/MM/YYYY'
        InputAdornmentProps={{ position: 'end' }}
      />
      <UsersAutocomplete
        onInputTextChange={(value) =>
          onFilterChange({ ...filter, userInputValue: value })
        }
        inputValue={filter.userInputValue}
        onChange={(e, option) => {
          if (!option) {
            onFilterChange({ ...filter, importedBy: undefined });
            return;
          }
          onFilterChange({ ...filter, importedBy: option.node.id });
        }}
        value={filter.importedBy}
      />
      <StyledFormControl variant='outlined' margin='dense'>
        <InputLabel>Status</InputLabel>
        <Select
          value={filter.status || ''}
          variant='outlined'
          label='Status'
          onChange={(e) => handleFilterChange(e, 'status')}
        >
          <MenuItem value=''>
            <em>None</em>
          </MenuItem>
          {registrationChoicesData.registrationDataStatusChoices.map((item) => {
            return (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            );
          })}
        </Select>
      </StyledFormControl>
    </Container>
  );
}
