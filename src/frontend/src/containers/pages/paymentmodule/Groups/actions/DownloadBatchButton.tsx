import { usePermissions } from '@hooks/usePermissions';
import { GetApp } from '@mui/icons-material';
import { Box, Button } from '@mui/material';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';

interface DownloadBatchButtonProps {
  groupId: string;
  tag: string;
}

export function DownloadBatchButton({
  groupId,
  tag,
}: DownloadBatchButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const permissions = usePermissions();

  if (
    !hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX, permissions)
  )
    return null;

  const href = `/api/download-payment-plan-group-batch/${groupId}/${tag}`;

  return (
    <Box m={2}>
      <Button
        component="a"
        href={href}
        download
        startIcon={<GetApp />}
        color="primary"
        variant="outlined"
        data-cy="button-download-batch"
      >
        {t('Download Batch')}
      </Button>
    </Box>
  );
}
