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
import type { PaymentPlanGroupCreate } from '@restgenerated/models/PaymentPlanGroupCreate';
import { RestService } from '@restgenerated/index';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import type { ReactElement } from 'react';
import { useState } from 'react';
import type { PaymentPlanGroupSettings } from './PaymentPlanGroupSettingsFields';
import { PaymentPlanGroupSettingsFields } from './PaymentPlanGroupSettingsFields';
import { useTranslation } from 'react-i18next';

interface CreatePaymentPlanGroupModalProps {
  open: boolean;
  onClose: () => void;
  cycleId: string;
  cycleTitle: string;
  onSuccess: (group: { id: string; name: string }) => void;
}

const emptySettings: PaymentPlanGroupSettings = {
  financialServiceProvider: null,
  currency: null,
};

export const CreatePaymentPlanGroupModal = ({
  open,
  onClose,
  cycleId,
  cycleTitle,
  onSuccess,
}: CreatePaymentPlanGroupModalProps): ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { businessArea, programId } = useBaseUrl();
  const queryClient = useQueryClient();
  const [groupName, setGroupName] = useState('');
  const [settings, setSettings] =
    useState<PaymentPlanGroupSettings>(emptySettings);

  const { mutateAsync: createGroup, isPending: creatingGroup } = useMutation({
    mutationFn: (name: string) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsCreate({
        businessAreaSlug: businessArea,
        programCode: programId,
        // Generated PaymentPlanGroupCreate marks readonly id/unicefId as
        // required; the endpoint doesn't accept them.
        requestBody: {
          name,
          cycle: cycleId,
          financialServiceProvider: settings.financialServiceProvider,
          currency: settings.currency,
        } as unknown as PaymentPlanGroupCreate,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlanGroupsList,
        ),
      });
    },
  });

  const handleClose = () => {
    setGroupName('');
    setSettings(emptySettings);
    onClose();
  };

  const handleCreate = async (): Promise<void> => {
    try {
      const result = await createGroup(groupName.trim());
      showMessage(t('Payment Plan Group created'));
      onSuccess({ id: result.id, name: result.name ?? groupName.trim() });
      setGroupName('');
      setSettings(emptySettings);
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogTitle>{t('Create Payment Plan Group')}</DialogTitle>
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
          label={t('Group Name')}
          name="groupName"
          fullWidth
          value={groupName}
          onChange={(e) => setGroupName(e.target.value)}
          data-cy="input-create-group-name"
        />
        <Box sx={{ mt: 2 }}>
          <PaymentPlanGroupSettingsFields
            value={settings}
            onChange={setSettings}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>{t('Cancel')}</Button>
        <Button
          onClick={handleCreate}
          variant="contained"
          disabled={!groupName.trim() || creatingGroup}
          data-cy="button-create-group-submit"
        >
          {t('Create')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
