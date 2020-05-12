import React, { useState } from 'react';
import styled from 'styled-components';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Typography,
} from '@material-ui/core';
import MergeTypeRoundedIcon from '@material-ui/icons/MergeTypeRounded';
import {
  RegistrationDetailedFragment,
  useMergeRdiMutation,
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

interface MergeRegistrationDataImportDialogProps {
  registration: RegistrationDetailedFragment;
}

export function MergeRegistrationDataImportDialog({
  registration,
}: MergeRegistrationDataImportDialogProps): React.ReactElement {
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate] = useMergeRdiMutation({
    variables: { id: registration.id },
  });
  const merge = async (): Promise<void> => {
    const { errors } = await mutate();
    if (errors) {
      showMessage('Error while merging Registration Data Import');
      return;
    }
    showMessage('Registration Data Import Merging started');
  };
  return (
    <span>
      <Button
        startIcon={<MergeTypeRoundedIcon />}
        color='primary'
        variant='contained'
        onClick={() => setOpen(true)}
      >
        Merge
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            <Typography variant='h6'>Merge Import</Typography>
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <div>Are your sure you want to merge this data import?</div>
            <div>
              <strong>
                {registration.numberOfHouseholds} households and{' '}
                {registration.numberOfIndividuals} individuals will be merged.{' '}
              </strong>
              Do you want to proceed?
            </div>
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>CANCEL</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={merge}
            >
              MERGE
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
}
