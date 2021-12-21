import {
  FormControl,
  Grid,
  InputAdornment,
  MenuItem,
  Paper,
} from '@material-ui/core';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import InputLabel from '../../shared/InputLabel';
import Select from '../../shared/Select';
import { useAllProgramsQuery } from '../../__generated__/graphql';
import { LoadingComponent } from '../LoadingComponent';
import { AdminAreaAutocomplete } from '../Population/AdminAreaAutocomplete';

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
const StyledFormControl = styled(FormControl)`
  width: 100%;
  color: #5f6368;
  border-bottom: 0;
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
  const { data, loading } = useAllProgramsQuery({
    variables: { businessArea },
  });
  if (loading) return <LoadingComponent />;

  const allPrograms = data?.allPrograms?.edges || [];
  const programs = allPrograms.map((edge) => edge.node);
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <Container>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>{t('Programme')}</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'program')}
              variant='outlined'
              label='Programme'
              value={filter.program || ''}
              InputProps={{
                startAdornment: (
                  <InputAdornment position='start'>
                    <FlashOnIcon />
                  </InputAdornment>
                ),
              }}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {programs.map((program) => (
                <MenuItem key={program.id} value={program.id}>
                  {program.name}
                </MenuItem>
              ))}
            </Select>
          </StyledFormControl>
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
