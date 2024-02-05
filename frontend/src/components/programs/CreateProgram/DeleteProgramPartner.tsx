import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { Delete } from '@material-ui/icons';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { DialogDescription } from '../../../containers/dialogs/DialogDescription';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';
import { GreyText } from '../../core/GreyText';
import { LoadingButton } from '../../core/LoadingButton';
import { ErrorButton } from '../../core/ErrorButton';

const WhiteDeleteIcon = styled(Delete)`
  color: #fff;
`;

interface DeleteProgramPartnerProps {
  canDeleteProgramPartner: boolean;
  handleDeleteProgramPartner;
}

export const DeleteProgramPartner = ({
  canDeleteProgramPartner,
  handleDeleteProgramPartner,
}: DeleteProgramPartnerProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);

  return (
    <>
      <ErrorButton
        data-cy="button-delete"
        onClick={() => setOpen(true)}
        disabled={!canDeleteProgramPartner}
      >
        <Delete />
      </ErrorButton>
      <Dialog open={open} onClose={() => setOpen(false)} scroll="paper">
        <DialogTitleWrapper>
          <DialogTitle>
            {t(
              'Are you sure you want to remove the partner from this program?',
            )}
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
              //TODO: fix this
              loading={false}
              type="submit"
              variant="contained"
              onClick={() => handleDeleteProgramPartner()}
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
