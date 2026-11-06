import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Typography,
} from '@mui/material';
import type { PaymentPlanCreate } from '@restgenerated/models/PaymentPlanCreate';
import { RestService } from '@restgenerated/index';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import type { ReactElement } from 'react';
import { useState } from 'react';
import type { PaymentPlanSettings } from './PaymentPlanSettingsFields';
import { PaymentPlanSettingsFields } from './PaymentPlanSettingsFields';
import { useTranslation } from 'react-i18next';

interface CreatePaymentPlanModalProps {
  open: boolean;
  onClose: () => void;
  cycleId: string;
  cycleTitle: string;
  onSuccess: (paymentPlan: { id: string; name: string }) => void;
}

const emptySettings: PaymentPlanSettings = {
  financialServiceProvider: null,
  currency: null,
  dispersionStartDate: null,
  dispersionEndDate: null,
};

export const CreatePaymentPlanModal = ({
  open,
  onClose,
  cycleId,
  cycleTitle,
  onSuccess,
}: CreatePaymentPlanModalProps): ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { businessArea, programId } = useBaseUrl();
  const queryClient = useQueryClient();
  const [paymentPlanName, setPaymentPlanName] = useState('');
  const [settings, setSettings] = useState<PaymentPlanSettings>(emptySettings);

  const { mutateAsync: createPaymentPlan, isPending: creatingPaymentPlan } =
    useMutation({
      mutationFn: (name: string) =>
        RestService.restBusinessAreasProgramsPaymentPlansCreate({
          businessAreaSlug: businessArea,
          programCode: programId,
          // Generated PaymentPlanCreate marks readonly id/unicefId as
          // required; the endpoint doesn't accept them.
          requestBody: {
            name,
            cycle: cycleId,
            financialServiceProvider: settings.financialServiceProvider,
            currency: settings.currency,
            dispersionStartDate: settings.dispersionStartDate,
            dispersionEndDate: settings.dispersionEndDate,
          } as unknown as PaymentPlanCreate,
        }),
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsPaymentPlansList,
          ),
        });
      },
    });

  const handleClose = () => {
    setPaymentPlanName('');
    setSettings(emptySettings);
    onClose();
  };

  const handleCreate = async (): Promise<void> => {
    try {
      const result = await createPaymentPlan(paymentPlanName.trim());
      showMessage(t('Payment Plan created'));
      onSuccess({ id: result.id, name: result.name ?? paymentPlanName.trim() });
      setPaymentPlanName('');
      setSettings(emptySettings);
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogTitle>{t('Create Payment Plan')}</DialogTitle>
      <DialogContent>
        <Box
          sx={{
            mb: 2,
          }}
        >
          <Typography variant="body2" color="textSecondary">
            {t('Cycle')}: <strong>{cycleTitle}</strong>
          </Typography>
        </Box>
        <TextField
          autoFocus
          margin="dense"
          label={t('Payment Plan Name')}
          name="groupName"
          fullWidth
          value={paymentPlanName}
          onChange={(e) => setPaymentPlanName(e.target.value)}
          data-cy="input-create-group-name"
        />
        <Box sx={{ mt: 2 }}>
          <PaymentPlanSettingsFields value={settings} onChange={setSettings} />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>{t('Cancel')}</Button>
        <Button
          onClick={handleCreate}
          variant="contained"
          disabled={!paymentPlanName.trim() || creatingPaymentPlan}
          data-cy="button-create-group-submit"
        >
          {t('Create')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
