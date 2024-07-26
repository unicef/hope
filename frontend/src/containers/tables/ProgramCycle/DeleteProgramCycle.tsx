import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import DeleteIcon from '@mui/icons-material/Delete';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@mui/material';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { DialogDescription } from '@containers/dialogs/DialogDescription';
import { GreyText } from '@core/GreyText';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { LoadingButton } from '@core/LoadingButton';

const WhiteDeleteIcon = styled(DeleteIcon)`
  color: #fff;
`;

interface DeleteProgramCycleProps {
  programCycle;
}

export const DeleteProgramCycle = ({
  programCycle,
}: DeleteProgramCycleProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);

  // TODO connect with API
  const handleDelete = (): void => {
    console.log('Delete program cycle', programCycle);
    setOpen(false);
  };

  const loading = false;

  return (
    <>
      <IconButton color="primary" onClick={() => setOpen(true)}>
        <DeleteIcon />
      </IconButton>
      <Dialog open={open} onClose={() => setOpen(false)} scroll="paper">
        <DialogTitleWrapper>
          <DialogTitle>
            {
              'Are you sure you want to delete the Program Cycle from the system?'
            }
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <GreyText>{t('This action cannot be undone.')}</GreyText>
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <LoadingButton
              loading={loading}
              error
              type="submit"
              variant="contained"
              onClick={handleDelete}
              data-cy="button-delete"
              endIcon={<WhiteDeleteIcon />}
            >
              {t('Delete')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
