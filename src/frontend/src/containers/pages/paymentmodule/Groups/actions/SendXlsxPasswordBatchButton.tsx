import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Lock } from '@mui/icons-material';
import { Box } from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

interface SendXlsxPasswordBatchButtonProps {
  groupId: string;
  tag: string;
}

export function SendXlsxPasswordBatchButton({
  groupId,
  tag,
}: SendXlsxPasswordBatchButtonProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();

  const { mutateAsync: sendPassword, isPending: loadingSend } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsSendXlsxPasswordCreate(
        {
          businessAreaSlug: businessArea,
          programCode: programId,
          id: groupId,
          requestBody: { exportTag: parseInt(tag, 10) },
        },
      ),
    onSuccess: () => {
      showMessage(t('Password has been sent.'));
    },
    onError: (error: any) => {
      showMessage(error?.message ?? t('Failed to send password'));
    },
  });

  return (
    <Box m={2}>
      <LoadingButton
        loading={loadingSend}
        startIcon={<Lock />}
        color="primary"
        variant="contained"
        onClick={() => sendPassword()}
        disabled={!groupId || !tag || loadingSend}
        data-cy="button-send-xlsx-password-batch"
      >
        {t('Send Xlsx Password')}
      </LoadingButton>
    </Box>
  );
}
