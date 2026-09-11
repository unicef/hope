import { LoadingButton } from '@core/LoadingButton';
import { useSnackbar } from '@hooks/useSnackBar';
import type { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import type { ReactElement } from 'react';
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
  mutationFn,
  successMessage,
  color = 'primary',
  variant = 'contained',
  dataCy,
}: SimpleWorkflowButtonProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync, isPending } = useMutation({
    mutationFn,
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsFollowUpInstructionsRetrieve,
        ),
      });
      await queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsFollowUpInstructionsList,
        ),
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
