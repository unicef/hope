import { Box, Grid, MenuItem } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import {
  AllProgramCyclesQueryVariables,
  useProgrammeChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { ClearApplyButtons } from '../../../../components/core/ClearApplyButtons';
import { ContainerWithBorder } from '../../../../components/core/ContainerWithBorder';
import { Missing } from '../../../../components/core/Missing';
import { NumberTextField } from '../../../../components/core/NumberTextField';
import { SearchTextField } from '../../../../components/core/SearchTextField';
import { SelectFilter } from '../../../../components/core/SelectFilter';
import { createHandleApplyFilterChange } from '../../../../utils/utils';

//TODO: add missing props
export type FilterProps = Pick<
  AllProgramCyclesQueryVariables,
  'search' | 'status'
>;

interface ProgramCyclesFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const ProgramCyclesFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: ProgramCyclesFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();

  const {
    handleFilterChange,
    applyFilterChanges,
    clearFilter,
  } = createHandleApplyFilterChange(
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

  const { data: programChoiceData } = useProgrammeChoiceDataQuery();

  if (!programChoiceData) {
    return null;
  }

  return (
    <ContainerWithBorder>
      <Grid container spacing={3} alignItems='flex-end'>
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            fullWidth
            onChange={(e) => handleFilterChange('search', e.target.value)}
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            variant='outlined'
            label={t('Status')}
            multiple
            value={filter.status}
            fullWidth
          >
            {programChoiceData.programCycleStatusChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <Box display='flex' flexDirection='column'>
            <Missing />
            <NumberTextField
              id='totalEntitledQuantityFromFilter'
              topLabel={t('Total Entitled Quantity')}
              value={filter.totalEntitledQuantityFrom}
              placeholder={t('From')}
              onChange={(e) =>
                handleFilterChange('totalEntitledQuantityFrom', e.target.value)
              }
            />
          </Box>
        </Grid>
        <Grid item xs={3}>
          <Box display='flex' flexDirection='column'>
            <NumberTextField
              id='totalEntitledQuantityToFilter'
              value={filter.totalEntitledQuantityTo}
              placeholder={t('To')}
              onChange={(e) =>
                handleFilterChange('totalEntitledQuantityTo', e.target.value)
              }
              error={
                filter.totalEntitledQuantityFrom &&
                filter.totalEntitledQuantityTo &&
                filter.totalEntitledQuantityFrom >
                  filter.totalEntitledQuantityTo
              }
            />
            <Missing />
          </Box>
        </Grid>
      </Grid>
      <ClearApplyButtons
        clearHandler={handleClearFilter}
        applyHandler={handleApplyFilter}
      />
    </ContainerWithBorder>
  );
};
