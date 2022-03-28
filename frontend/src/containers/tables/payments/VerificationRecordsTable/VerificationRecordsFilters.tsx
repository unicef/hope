import {
  Box,
  Button,
  Collapse,
  FormControl,
  Grid,
  InputAdornment,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
} from '@material-ui/core';
import { KeyboardArrowDown, KeyboardArrowUp } from '@material-ui/icons';
import SearchIcon from '@material-ui/icons/Search';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { usePaymentVerificationChoicesQuery } from '../../../../__generated__/graphql';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;

  flex-direction: row;
  align-items: center;

  && > div {
    margin: 5px;
  }
`;
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

interface VerificationRecordsFiltersProps {
  onFilterChange;
  filter;
  verifications;
}
export function VerificationRecordsFilters({
  onFilterChange,
  filter,
  verifications,
}: VerificationRecordsFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const [show, setShow] = useState(false);
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
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
      <Container>
        <Collapse in={show}>
          <Grid container spacing={3}>
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
                data-cy='filters-search'
              />
            </Grid>
            <Grid item>
              <StyledFormControl variant='outlined' margin='dense'>
                <InputLabel>{t('Verification Status')}</InputLabel>
                <Select
                  /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
                  // @ts-ignore
                  onChange={(e) => handleFilterChange(e, 'status')}
                  variant='outlined'
                  label={t('Verification Status')}
                  value={filter.status || ''}
                >
                  <MenuItem value=''>
                    <em>None</em>
                  </MenuItem>
                  {choicesData.paymentVerificationStatusChoices.map((item) => {
                    return (
                      <MenuItem key={item.value} value={item.value}>
                        {item.name}
                      </MenuItem>
                    );
                  })}
                </Select>
              </StyledFormControl>
            </Grid>
            <Grid item>
              <StyledFormControl variant='outlined' margin='dense'>
                <InputLabel>{t('Verification Channel')}</InputLabel>
                <Select
                  /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
                  // @ts-ignore
                  onChange={(e) => handleFilterChange(e, 'verificationChannel')}
                  variant='outlined'
                  label={t('Verification Channel')}
                  value={filter.verificationChannel || ''}
                >
                  <MenuItem value=''>
                    <em>None</em>
                  </MenuItem>
                  {choicesData.cashPlanVerificationVerificationChannelChoices.map(
                    (item) => {
                      return (
                        <MenuItem key={item.value} value={item.value}>
                          {item.name}
                        </MenuItem>
                      );
                    },
                  )}
                </Select>
              </StyledFormControl>
            </Grid>
            <Grid item>
              <StyledFormControl variant='outlined' margin='dense'>
                <InputLabel>{t('Verification Plan Id')}</InputLabel>
                <Select
                  /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
                  // @ts-ignore
                  onChange={(e) =>
                    handleFilterChange(e, 'cashPlanPaymentVerification')
                  }
                  variant='outlined'
                  label={t('Verification Plan Id')}
                  value={filter.cashPlanPaymentVerification || ''}
                >
                  <MenuItem value=''>
                    <em>None</em>
                  </MenuItem>
                  {verificationPlanOptions}
                </Select>
              </StyledFormControl>
            </Grid>
          </Grid>
        </Collapse>
      </Container>
    </>
  );
}
