import { Grid, InputAdornment, MenuItem } from '@material-ui/core';
import FormControl from '@material-ui/core/FormControl';
import SearchIcon from '@material-ui/icons/Search';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ContainerWithBorder } from '../../../../components/core/ContainerWithBorder';
import InputLabel from '../../../../shared/InputLabel';
import Select from '../../../../shared/Select';
import TextField from '../../../../shared/TextField';
import { useCashPlanVerificationStatusChoicesQuery } from '../../../../__generated__/graphql';

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

interface FspFiltersProps {
  onFilterChange;
  filter;
}
export function FspFilters({
  onFilterChange,
  filter,
}: FspFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  const {
    data: statusChoicesData,
  } = useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) {
    return null;
  }

  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
            variant='outlined'
            margin='dense'
            onChange={(e) => handleFilterChange(e, 'search')}
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>{t('Payment Channel')}</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'paymentChannel')}
              variant='outlined'
              label='Modality'
              value={filter.paymentChannel || ''}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {statusChoicesData.paymentRecordDeliveryTypeChoices.map(
                (item) => (
                  <MenuItem key={item.name} value={item.value}>
                    {item.name}
                  </MenuItem>
                ),
              )}
            </Select>
          </StyledFormControl>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
