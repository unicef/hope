import React, { useState } from 'react';
import styled from 'styled-components';
import {
  InputAdornment,
  TextField,
  Grid,
  Typography,
  Box,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import { KeyboardArrowDown, KeyboardArrowUp } from '@material-ui/icons';
import { useCashPlanVerificationStatusChoicesQuery } from '../../../__generated__/graphql';

const Container = styled.div`
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
  const [show, setShow] = useState(false);
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  const {
    data: statusChoicesData,
  } = useCashPlanVerificationStatusChoicesQuery();
  if (!statusChoicesData) {
    return null;
  }
  return (
    <>
      <Box display='flex' justifyContent='space-between'>
        <Typography variant='h6'>Filters</Typography>
        {show ? (
          <Button
            endIcon={<KeyboardArrowUp />}
            color='primary'
            variant='outlined'
            onClick={() => setShow(false)}
            data-cy='button-show'
          >
            HIDE
          </Button>
        ) : (
          <Button
            endIcon={<KeyboardArrowDown />}
            color='primary'
            variant='outlined'
            onClick={() => setShow(true)}
            data-cy='button-show'
          >
            SHOW
          </Button>
        )}
      </Box>
      <Container>
        {show ? (
          <Grid container spacing={3}>
            <Grid item xs={3}>
              <SearchTextField
                label='Search'
                variant='outlined'
                margin='dense'
                onChange={(e) => handleFilterChange(e, 'text')}
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
            <Grid item xs={3}>
              <StyledFormControl variant='outlined' margin='dense'>
                <InputLabel>Verification Status</InputLabel>
                <Select
                  /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
                  // @ts-ignore
                  onChange={(e) => handleFilterChange(e, 'verificationStatus')}
                  variant='outlined'
                  label='Verification Status'
                  value={filter.verificationStatus || ''}
                >
                  <MenuItem value=''>
                    <em>None</em>
                  </MenuItem>
                  {statusChoicesData.cashPlanVerificationStatusChoices.map(
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
