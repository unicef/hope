import { Grid, InputAdornment, MenuItem } from '@material-ui/core';
import FormControl from '@material-ui/core/FormControl';
import SearchIcon from '@material-ui/icons/Search';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ContainerWithBorder } from '../../../../components/core/ContainerWithBorder';
import { SearchTextField } from '../../../../components/core/SearchTextField';
import { SelectFilter } from '../../../../components/core/SelectFilter';
import InputLabel from '../../../../shared/InputLabel';
import Select from '../../../../shared/Select';
import TextField from '../../../../shared/TextField';
import { useCashPlanVerificationStatusChoicesQuery } from '../../../../__generated__/graphql';

interface FspFiltersProps {
  onFilterChange;
  filter;
}
export const FspFilters = ({
  onFilterChange,
  filter,
}: FspFiltersProps): React.ReactElement => {
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
            onChange={(e) => handleFilterChange(e, 'search')}
            value={filter.search}
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'paymentChannel')}
            variant='outlined'
            label={t('Payment Channel')}
            value={filter.paymentChannel || ''}
          >
            <MenuItem value=''>
              <em>None</em>
            </MenuItem>
            {statusChoicesData.paymentRecordDeliveryTypeChoices.map((item) => (
              <MenuItem key={item.name} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
};
