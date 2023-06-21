import { Grid, Paper } from '@material-ui/core';
import React from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { AdminAreaAutocomplete } from '../../shared/autocompletes/AdminAreaAutocomplete';
import { createHandleApplyFilterChange } from '../../utils/utils';
import { ClearApplyButtons } from '../core/ClearApplyButtons';

const Container = styled(Paper)`
  display: flex;
  flex-direction: column;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  align-items: center;
  && > div {
    margin: 5px;
  }
`;

interface DashboardFiltersProps {
  filter;
  setFilter;
  initialFilter;
  appliedFilter;
  setAppliedFilter;
}

export const DashboardFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: DashboardFiltersProps): React.ReactElement => {
  const history = useHistory();
  const location = useLocation();
  const { applyFilterChanges, clearFilter } = createHandleApplyFilterChange(
    initialFilter,
    history,
    location,
    filter,
    setFilter,
    appliedFilter,
    setAppliedFilter,
  );
  const handleApplyFilter = (): void => {
    applyFilterChanges();
  };

  const handleClearFilter = (): void => {
    clearFilter();
  };

  return (
    <Container>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={5}>
          <AdminAreaAutocomplete
            fullWidth
            name='administrativeArea'
            value={filter.administrativeArea}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </Grid>
      </Grid>
      <ClearApplyButtons
        applyHandler={handleApplyFilter}
        clearHandler={handleClearFilter}
      />
    </Container>
  );
};
