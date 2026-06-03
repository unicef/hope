import { GetApp } from '@mui/icons-material';
import { Box, Button } from '@mui/material';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

interface DownloadBatchButtonProps {
  exportFileLink: string | null;
}

export function DownloadBatchButton({
  exportFileLink,
}: DownloadBatchButtonProps): ReactElement {
  const { t } = useTranslation();

  // TODO: The backend plans a dedicated /download-payment-plan-group-batch endpoint
  // (not nested under payment-plan-groups). Once it exists, regenerate REST types
  // and replace this direct-link approach with the RestService method if needed.
  // For now we use the exportFileLink URL directly, consistent with FollowUpInstruction.
  return (
    <Box m={2}>
      <Button
        component="a"
        href={exportFileLink ?? undefined}
        download
        startIcon={<GetApp />}
        color="primary"
        variant="outlined"
        disabled={!exportFileLink}
        data-cy="button-download-batch"
      >
        {t('Download Batch')}
      </Button>
    </Box>
  );
}
