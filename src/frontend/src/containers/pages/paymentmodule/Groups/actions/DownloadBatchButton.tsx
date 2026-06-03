import { GetApp } from '@mui/icons-material';
import { Box, Button } from '@mui/material';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

interface DownloadBatchButtonProps {
  groupId: string;
  tag: string;
}

export function DownloadBatchButton({
  groupId,
  tag,
}: DownloadBatchButtonProps): ReactElement {
  const { t } = useTranslation();

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
