import React, { useState } from 'react';
import styled from 'styled-components';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import {
  RegistrationDetailedFragment,
  useUnapproveRdiMutation,
} from '../../../__generated__/graphql';
import { useSnackbar } from '../../../hooks/useSnackBar';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

interface UnapproveRegistrationDataImportDialogProps {
  registration: RegistrationDetailedFragment;
}

export function UnapproveRegistrationDataImportDialog({
  registration,
}: UnapproveRegistrationDataImportDialogProps): React.ReactElement {
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate] = useUnapproveRdiMutation({
    variables: { id: registration.id },
  });
  const approve = async (): Promise<void> => {
    const { errors } = await mutate();
    if (errors) {
      showMessage('Error while unapproving Registration Data Import');
      return;
    }
    showMessage('Registration Data Import Unapproved');
  };
  return (
    <span>
      <Button color='primary' variant='outlined' onClick={() => setOpen(true)}>
        Unapprove
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            <Typography variant='h6'>
              Unapprove Registration Data Import
            </Typography>
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            Do you want to unapprove {registration.name} Registration Data
            Import
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>CANCEL</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={approve}
            >
              UNAPPROVE
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
}
