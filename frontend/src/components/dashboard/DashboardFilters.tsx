import { Grid, MenuItem, Paper } from '@material-ui/core';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useAllProgramsForChoicesQuery } from '../../__generated__/graphql';
import { LoadingComponent } from '../core/LoadingComponent';
import { SelectFilter } from '../core/SelectFilter';
import { AdminAreaAutocomplete } from '../population/AdminAreaAutocomplete';

const Container = styled(Paper)`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: row;
  align-items: center;
  && > div {
    margin: 5px;
  }
`;

interface DashboardFiltersProps {
  onFilterChange;
  filter;
}

export const DashboardFilters = ({
  onFilterChange,
  filter,
}: DashboardFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const { data, loading } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });
  if (loading) return <LoadingComponent />;

  const allPrograms = data?.allPrograms?.edges || [];
  const programs = allPrograms.map((edge) => edge.node);
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <Container>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'program')}
            label={t('Programme')}
            value={filter.program || ''}
            icon={<FlashOnIcon />}
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
            {programs.map((program) => (
              <MenuItem key={program.id} value={program.id}>
                {program.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <AdminAreaAutocomplete
            fullWidth
            onFilterChange={onFilterChange}
            name='administrativeArea'
          />
        </Grid>
      </Grid>
    </Container>
  );
};
