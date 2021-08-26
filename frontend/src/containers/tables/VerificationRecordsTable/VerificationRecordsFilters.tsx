import {
  Box,
  Button,
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
import { usePaymentVerificationStatusChoicesQuery } from '../../../__generated__/graphql';

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
}
export function VerificationRecordsFilters({
  onFilterChange,
  filter,
}: VerificationRecordsFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const [show, setShow] = useState(false);
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  const {
    data: statusChoicesData,
  } = usePaymentVerificationStatusChoicesQuery();
  if (!statusChoicesData) {
    return null;
  }
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
        {show ? (
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
                  {statusChoicesData.paymentVerificationStatusChoices.map(
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
          </Grid>
        ) : null}
      </Container>
    </>
  );
}
