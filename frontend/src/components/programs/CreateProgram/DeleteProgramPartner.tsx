import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { DialogDescription } from '../../../containers/dialogs/DialogDescription';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';
import { ErrorButton } from '../../core/ErrorButton';
import { GreyText } from '../../core/GreyText';
import { LoadingButton } from '../../core/LoadingButton';

const WhiteDeleteIcon = styled(Delete)`
  color: #fff;
`;

interface DeleteProgramPartnerProps {
  canDeleteProgramPartner: boolean;
  handleDeleteProgramPartner;
  partner;
}

export const DeleteProgramPartner = ({
  canDeleteProgramPartner,
  handleDeleteProgramPartner,
  partner,
}: DeleteProgramPartnerProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);

  return (
    <>
      <ErrorButton
        variant='outlined'
        onClick={() => setOpen(true)}
        disabled={!canDeleteProgramPartner}
      >
        <Delete />
      </ErrorButton>
      <Dialog open={open} onClose={() => setOpen(false)} scroll='paper'>
        <DialogTitleWrapper>
          <DialogTitle>
            {`Are you sure you want to delete the Program Partner #${partner.id}`}
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
              error
              type='submit'
              variant='contained'
              onClick={() => handleDeleteProgramPartner(partner.id)}
              data-cy='button-delete'
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
