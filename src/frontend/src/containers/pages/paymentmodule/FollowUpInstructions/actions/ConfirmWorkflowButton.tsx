import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
} from '@mui/material';
import { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';

interface ConfirmWorkflowButtonProps {
  label: string;
  instruction: FollowUpInstructionDetail;
  mutationFn: (comment?: string) => Promise<unknown>;
  successMessage: string;
  withComment?: boolean;
  confirmMessage?: string;
  color?: 'primary' | 'secondary' | 'error' | 'inherit';
  variant?: 'contained' | 'outlined' | 'text';
  dataCy?: string;
}

export function ConfirmWorkflowButton({
  label,
  instruction,
  mutationFn,
  successMessage,
  withComment = false,
  confirmMessage,
  color = 'primary',
  variant = 'contained',
  dataCy,
}: ConfirmWorkflowButtonProps): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [comment, setComment] = useState('');
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync, isPending } = useMutation({
    mutationFn: () => mutationFn(comment || undefined),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: [
          'followUpInstruction',
          businessArea,
          instruction.id,
          programId,
        ],
      });
      await queryClient.invalidateQueries({
        queryKey: ['followUpInstructionsList', businessArea, programId],
      });
      setOpen(false);
      setComment('');
      showMessage(t(successMessage));
    },
    onError: (e) => {
      showApiErrorMessages(e, showMessage);
    },
  });

  return (
    <>
      <Button
        variant={variant}
        color={color}
        onClick={() => setOpen(true)}
        data-cy={dataCy}
      >
        {t(label)}
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitleWrapper>
          <DialogTitle>{t(label)}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          {confirmMessage && <p>{t(confirmMessage)}</p>}
          {withComment && (
            <TextField
              label={t('Comment')}
              multiline
              rows={3}
              fullWidth
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              variant="outlined"
            />
          )}
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <LoadingButton
              loading={isPending}
              color={color}
              variant="contained"
              onClick={() => mutateAsync()}
              data-cy={`${dataCy}-confirm`}
            >
              {t('Confirm')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
