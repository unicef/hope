import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Lock } from '@mui/icons-material';
import { Box } from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import type { PaymentPlanGroupDetail } from '../types';

interface SendXlsxPasswordGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function SendXlsxPasswordGroupButton({
  group,
}: SendXlsxPasswordGroupButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();

  const { mutate: sendPassword, isPending: loadingSend } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsSendXlsxPasswordCreate(
        {
          businessAreaSlug: businessArea,
          programCode: programId,
          id: group?.id ?? '',
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
  if (!group?.exportFileHasPassword) return null;

  return (
    <Box
      sx={{
        m: 2,
      }}
    >
      <LoadingButton
        loading={loadingSend}
        startIcon={<Lock />}
        color="primary"
        variant="contained"
        onClick={() => sendPassword()}
        disabled={loadingSend}
        data-cy="button-send-xlsx-password-group"
      >
        {t('Send Xlsx Password')}
      </LoadingButton>
    </Box>
  );
}
