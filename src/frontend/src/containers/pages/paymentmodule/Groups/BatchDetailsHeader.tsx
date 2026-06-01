import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box } from '@mui/material';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { DownloadBatchButton } from './actions/DownloadBatchButton';
import { ExportBatchButton } from './actions/ExportBatchButton';

interface BatchDetailsHeaderProps {
  groupId: string;
  tag: string;
}

export function BatchDetailsHeader({
  groupId,
  tag,
}: BatchDetailsHeaderProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/program-cycles`,
    },
    {
      title: t('Groups'),
      to: `/${baseUrl}/payment-module/groups`,
    },
    {
      title: t('Group'),
      to: `/${baseUrl}/payment-module/groups/${groupId}`,
    },
  ];

  return (
    <PageHeader
      title={
        <Box display="flex" alignItems="baseline" gap={1}>
          <Box>{t('Batch')}</Box>
          <Box color="text.secondary" fontSize="0.85em">
            {tag}
          </Box>
        </Box>
      }
      breadCrumbs={breadCrumbsItems}
    >
      <Box display="flex" alignItems="center">
        <DownloadBatchButton groupId={groupId} tag={tag} />
        <ExportBatchButton groupId={groupId} tag={tag} />
      </Box>
    </PageHeader>
  );
}
