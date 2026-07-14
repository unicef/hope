import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

interface SimpleWorkflowButtonProps {
  label: string;
  instruction: FollowUpInstructionDetail;
  mutationFn: () => Promise<unknown>;
  successMessage: string;
  color?: 'primary' | 'secondary' | 'error' | 'inherit';
  variant?: 'contained' | 'outlined' | 'text';
  dataCy?: string;
}

export function SimpleWorkflowButton({
  label,
  instruction,
  mutationFn,
  successMessage,
  color = 'primary',
  variant = 'contained',
  dataCy,
}: SimpleWorkflowButtonProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync, isPending } = useMutation({
    mutationFn,
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
      showMessage(t(successMessage));
    },
    onError: (e) => {
      showApiErrorMessages(e, showMessage);
    },
  });

  return (
    <LoadingButton
      loading={isPending}
      color={color}
      variant={variant}
      onClick={() => mutateAsync()}
      data-cy={dataCy}
    >
      {t(label)}
    </LoadingButton>
  );
}
