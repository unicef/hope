import React from 'react';
import styled from 'styled-components';
import { InputAdornment, Grid } from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
// import TextField from '../../../shared/TextField';
import TextField from '../../shared/TextField';
import { ContainerWithBorder } from '../ContainerWithBorder';
// import { AdminAreasAutocomplete } from './AdminAreaAutocomplete';

const SearchTextField = styled(TextField)`
  flex: 1;
  && {
    min-width: 150px;
  }
`;

interface UsersListFiltersProps {
  onFilterChange;
  filter;
}
export function UsersListFilters({
  onFilterChange,
  filter,
}: UsersListFiltersProps): React.ReactElement {
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });

  return (
    <ContainerWithBorder>
      <Grid container spacing={3}>
        <Grid item>
          <SearchTextField
            label='Search'
            variant='outlined'
            margin='dense'
            onChange={(e) => handleFilterChange(e, 'fullName')}
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
