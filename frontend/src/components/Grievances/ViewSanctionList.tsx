import {
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  InputAdornment,
  TextField,
} from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
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
  const { t } = useTranslation();
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
        {t('VIEW SANCTION LIST')}
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
          <DialogTitle id='scroll-dialog-title'>
            {t('Sanction List View')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box mb={3}>
            <Grid container spacing={3}>
              <Grid item>
                <SearchTextField
                  label={t('Reference Number')}
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
                  label={t('Full Name')}
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
              {t('CLOSE')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
