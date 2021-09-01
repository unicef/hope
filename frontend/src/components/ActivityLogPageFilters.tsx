import { Grid, InputAdornment, MenuItem } from '@material-ui/core';
import FormControl from '@material-ui/core/FormControl';
import SearchIcon from '@material-ui/icons/Search';
import ViewModuleRoundedIcon from '@material-ui/icons/ViewModuleRounded';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import InputLabel from '../shared/InputLabel';
import Select from '../shared/Select';
import TextField from '../shared/TextField';
import { ContainerWithBorder } from './ContainerWithBorder';

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

interface ActivityLogPageFiltersProps {
  onFilterChange;
  filter;
}
export function ActivityLogPageFilters({
  onFilterChange,
  filter,
}: ActivityLogPageFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });

  const modules = {
    program: 'Programme',
    household: 'Household',
    individual: 'Individual',
    grievanceticket: 'Grievance ticket',
    cashplanpaymentverification: 'Cash plan payment verification',
    targetpopulation: 'Target Population',
    registrationdataimport: 'Registration data import',
  };
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
            variant='outlined'
            value={filter.search || ''}
            margin='dense'
            onChange={(e) => handleFilterChange(e, 'search')}
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>{t('Module')}</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'module')}
              variant='outlined'
              label={t('Module')}
              value={filter.module || ''}
              InputProps={{
                startAdornment: (
                  <StartInputAdornment position='start'>
                    <ViewModuleRoundedIcon />
                  </StartInputAdornment>
                ),
              }}
              SelectDisplayProps={{
                'data-cy': 'filters-residence-status',
              }}
              MenuProps={{
                'data-cy': 'filters-residence-status-options',
              }}
            >
              <MenuItem value=''>
                <em>{t('None')}</em>
              </MenuItem>
              {Object.entries(modules).map(([key, value]) => (
                <MenuItem key={key} value={key}>
                  {value}
                </MenuItem>
              ))}
            </Select>
          </StyledFormControl>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
