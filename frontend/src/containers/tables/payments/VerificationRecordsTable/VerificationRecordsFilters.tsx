import {
  Box,
  Button,
  Collapse,
  Grid,
  MenuItem,
  Typography,
} from '@material-ui/core';
import { KeyboardArrowDown, KeyboardArrowUp } from '@material-ui/icons';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { usePaymentVerificationChoicesQuery } from '../../../../__generated__/graphql';
import { ClearApplyButtons } from '../../../../components/core/ClearApplyButtons';
import { SearchTextField } from '../../../../components/core/SearchTextField';
import { SelectFilter } from '../../../../components/core/SelectFilter';
import { createHandleApplyFilterChange } from '../../../../utils/utils';

interface VerificationRecordsFiltersProps {
  filter;
  verifications;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const VerificationRecordsFilters = ({
  filter,
  verifications,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: VerificationRecordsFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const [show, setShow] = useState(false);
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
  const { data: choicesData } = usePaymentVerificationChoicesQuery();
  if (!choicesData) {
    return null;
  }

  const verificationPlanOptions = verifications.edges.map((item) => {
    return (
      <MenuItem key={item.node.unicefId} value={item.node.id}>
        {item.node.unicefId}
      </MenuItem>
    );
  });

  return (
    <>
      <Box display='flex' justifyContent='space-between'>
        <Typography variant='h6'>{t('Filters')}</Typography>
        {show ? (
          <Button
            endIcon={<KeyboardArrowUp />}
            color='primary'
            variant='outlined'
            onClick={() => setShow(false)}
            data-cy='button-show'
          >
            {t('HIDE')}
          </Button>
        ) : (
          <Button
            endIcon={<KeyboardArrowDown />}
            color='primary'
            variant='outlined'
            onClick={() => setShow(true)}
            data-cy='button-show'
          >
            {t('SHOW')}
          </Button>
        )}
      </Box>
      <Box>
        <Collapse in={show}>
          <Grid container spacing={3}>
            <Grid item xs={3}>
              <SearchTextField
                value={filter.search}
                label={t('Search')}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                data-cy='filters-search'
                fullWidth
              />
            </Grid>
            <Grid item xs={3}>
              <SelectFilter
                onChange={(e) => handleFilterChange('status', e.target.value)}
                label={t('Verification Status')}
                value={filter.status}
                fullWidth
              >
                {choicesData.paymentVerificationStatusChoices.map((item) => {
                  return (
                    <MenuItem key={item.value} value={item.value}>
                      {item.name}
                    </MenuItem>
                  );
                })}
              </SelectFilter>
            </Grid>
            <Grid item xs={3}>
              <SelectFilter
                onChange={(e) =>
                  handleFilterChange('verificationChannel', e.target.value)
                }
                label={t('Verification Channel')}
                value={filter.verificationChannel}
              >
                {choicesData.cashPlanVerificationVerificationChannelChoices.map(
                  (item) => {
                    return (
                      <MenuItem key={item.value} value={item.value}>
                        {item.name}
                      </MenuItem>
                    );
                  },
                )}
              </SelectFilter>
            </Grid>
            <Grid item xs={3}>
              <SelectFilter
                onChange={(e) =>
                  handleFilterChange('paymentVerificationPlan', e.target.value)
                }
                label={t('Verification Plan Id')}
                value={filter.paymentVerificationPlan}
              >
                {verificationPlanOptions}
              </SelectFilter>
            </Grid>
          </Grid>
          <ClearApplyButtons
            clearHandler={handleClearFilter}
            applyHandler={handleApplyFilter}
          />
        </Collapse>
      </Box>
    </>
  );
};
