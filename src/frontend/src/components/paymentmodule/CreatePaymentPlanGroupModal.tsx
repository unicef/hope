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
import { RestService } from '@restgenerated/index';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';

interface CreatePaymentPlanGroupModalProps {
  open: boolean;
  onClose: () => void;
  cycleId: string;
  cycleTitle: string;
  onSuccess: (group: { id: string; name: string }) => void;
}

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

  const { mutateAsync: createGroup, isPending: creatingGroup } = useMutation({
    mutationFn: (name: string) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsCreate({
        businessAreaSlug: businessArea,
        programCode: programId,
        requestBody: { name, cycle: cycleId } as any,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroupsList', businessArea, programId],
      });
    },
  });

  const handleClose = () => {
    setGroupName('');
    onClose();
  };

  const handleCreate = async (): Promise<void> => {
    try {
      const result = await createGroup(groupName.trim());
      showMessage(t('Payment Plan Group created'));
      onSuccess({ id: result.id, name: result.name ?? groupName.trim() });
      setGroupName('');
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogTitle>{t('Create Payment Plan Group')}</DialogTitle>
      <DialogContent>
        <Box mb={2}>
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
