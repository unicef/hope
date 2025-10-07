import {
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
} from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useDebounce } from '@hooks/useDebounce';
import { SearchTextField } from '@core/SearchTextField';
import { SanctionListIndividualsTable } from './SanctionListIndividualsTable/SanctionListIndividualsTable';

export function ViewSanctionList({
  referenceNumber,
}: {
  referenceNumber: string;
}): ReactElement {
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
      <Button color="primary" onClick={() => setDialogOpen(true)}>
        {t('VIEW SANCTION LIST')}
      </Button>
      <Dialog
        fullWidth
        maxWidth="md"
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Sanction List View')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box mb={3}>
            <Grid container spacing={3}>
              <Grid>
                <SearchTextField
                  label={t('Reference Number')}
                  value={filter.referenceNumber}
                  onChange={(e) => handleFilterChange(e, 'referenceNumber')}
                  data-cy="filters-search"
                />
              </Grid>
              <Grid>
                <SearchTextField
                  label={t('Full Name')}
                  value={filter.fullName}
                  onChange={(e) => handleFilterChange(e, 'fullName')}
                  data-cy="filters-search"
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
}
