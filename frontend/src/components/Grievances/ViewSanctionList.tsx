import React, { useState } from 'react';
import {
  Button,
  DialogContent,
  DialogTitle,
  DialogActions,
  Grid,
  InputAdornment,
  TextField,
  Box,
} from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import styled from 'styled-components';
import { Dialog } from '../../containers/dialogs/Dialog';
import { useDebounce } from '../../hooks/useDebounce';
import { SanctionListIndividualsTable } from './SanctionListIndividualsTable/SanctionListIndividualsTable';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;
const SearchTextField = styled(TextField)`
  flex: 1;
  && {
    min-width: 150px;
  }
`;

export const ViewSanctionList = ({
  referenceNumber,
}: {
  referenceNumber: string;
}): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const initialFilter = {
    fullName: '',
    referenceNumber,
  };
  const [filter, setFilter] = useState({
    fullName: '',
    referenceNumber,
  });

  const debouncedFilter = useDebounce(filter, 500);

  const handleFilterChange = (e, name): void =>
    setFilter({ ...filter, [name]: e.target.value });
  return (
    <>
      <Button color='primary' onClick={() => setDialogOpen(true)}>
        VIEW SANCTION LIST
      </Button>
      <Dialog
        fullWidth
        maxWidth='md'
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>Sanction List View</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box mb={3}>
            <Grid container spacing={3}>
              <Grid item>
                <SearchTextField
                  label='Reference Number'
                  value={filter.referenceNumber}
                  variant='outlined'
                  margin='dense'
                  onChange={(e) => handleFilterChange(e, 'referenceNumber')}
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
                <SearchTextField
                  label='Full Name'
                  value={filter.fullName}
                  variant='outlined'
                  margin='dense'
                  onChange={(e) => handleFilterChange(e, 'fullName')}
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
            </Grid>
          </Box>
          <SanctionListIndividualsTable filter={debouncedFilter} />
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button
              onClick={() => {
                setFilter(initialFilter);
                setDialogOpen(false);
              }}
            >
              CLOSE
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
