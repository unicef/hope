import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import {
  PaymentPlanQuery,
  useDeletePpMutation,
} from '../../../../__generated__/graphql';
import { DialogContainer } from '../../../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { getPaymentPlanUrlPart } from '../../../../utils/utils';
import { LoadingButton } from '../../../core/LoadingButton';

export interface DeletePaymentPlanProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const DeletePaymentPlan = ({
  paymentPlan,
}: DeletePaymentPlanProps): React.ReactElement => {
  const { t } = useTranslation();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const { baseUrl } = useBaseUrl();
  const history = useHistory();
  const [mutate, { loading: loadingDelete }] = useDeletePpMutation();
  const { id } = paymentPlan;

  const handleDelete = (): void => {
    mutate({
      variables: {
        paymentPlanId: id,
      },
    });
    history.push(
      `/${baseUrl}/payment-module/${getPaymentPlanUrlPart(
        paymentPlan.isFollowUp,
      )}/`,
    );
  };

  return (
    <>
      <Box p={2}>
        <IconButton
          data-cy='button-delete-payment-plan'
          onClick={() => setDeleteDialogOpen(true)}
        >
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
          <DialogTitle>{t('Delete Payment Plan')}</DialogTitle>
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
            <Button
              data-cy='button-cancel'
              onClick={() => setDeleteDialogOpen(false)}
            >
              CANCEL
            </Button>
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
