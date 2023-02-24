import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@material-ui/core';
import { useHistory } from 'react-router-dom';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Delete } from '@material-ui/icons';
import { DialogContainer } from '../../../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import {
  PaymentPlanQuery,
  useDeletePpMutation,
} from '../../../../__generated__/graphql';
import { LoadingButton } from '../../../core/LoadingButton';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';

export interface DeletePaymentPlanProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const DeletePaymentPlan = ({
  paymentPlan,
}: DeletePaymentPlanProps): React.ReactElement => {
  const { t } = useTranslation();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const businessArea = useBusinessArea();
  const history = useHistory();
  const [mutate, { loading: loadingDelete }] = useDeletePpMutation();
  const { id } = paymentPlan;

  const handleDelete = (): void => {
    mutate({
      variables: {
        paymentPlanId: id,
      },
    });
    history.push(`/${businessArea}/payment-module`);
  };

  return (
    <>
      <Box p={2}>
        <IconButton onClick={() => setDeleteDialogOpen(true)}>
          <Delete />
        </IconButton>
      </Box>
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            {t('Delete Payment Plan')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              {t('Are you sure you want to delete this Payment Plan?')}
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setDeleteDialogOpen(false)}>CANCEL</Button>
            <LoadingButton
              loading={loadingDelete}
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => handleDelete()}
              data-cy='button-submit'
            >
              {t('Delete')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
