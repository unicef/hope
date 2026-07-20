import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Lock } from '@mui/icons-material';
import { Box } from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';

interface SendXlsxPasswordBatchButtonProps {
  groupId: string;
  tag: string;
}

export function SendXlsxPasswordBatchButton({
  groupId,
  tag,
}: SendXlsxPasswordBatchButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();

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
    onError: (error) => {
      showApiErrorMessages(error, showMessage, t('Failed to send password'));
    },
  });

  if (!hasPermissions(PERMISSIONS.PM_SEND_XLSX_PASSWORD, permissions))
    return null;

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
