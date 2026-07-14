import { AdminButton } from '@components/core/AdminButton';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { StatusBox } from '@components/core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box, Button } from '@mui/material';
import GetAppIcon from '@mui/icons-material/GetApp';
import { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import {
  paymentPlanBackgroundActionStatusToColor,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { FollowUpInstructionActions } from './actions/FollowUpInstructionActions';

interface FollowUpInstructionDetailsHeaderProps {
  instruction: FollowUpInstructionDetail;
  permissions: string[];
}

export function FollowUpInstructionDetailsHeader({
  instruction,
  permissions,
}: FollowUpInstructionDetailsHeaderProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/program-cycles`,
    },
    {
      title: t('Follow-up Instructions'),
      to: `/${baseUrl}/payment-module/follow-up-instructions`,
    },
  ];

  return (
    <PageHeader
      title={
        <Box display="flex" alignItems="baseline" gap={1}>
          <Box>{instruction.unicefId ?? t('Follow-up Instruction')}</Box>
          <Box ml={1}>
            <StatusBox
              status={instruction.status}
              statusToColor={paymentPlanStatusToColor}
            />
          </Box>
          {instruction.backgroundActionStatus && (
            <Box>
              <StatusBox
                status={instruction.backgroundActionStatus}
                statusToColor={paymentPlanBackgroundActionStatusToColor}
              />
            </Box>
          )}
        </Box>
      }
      breadCrumbs={breadCrumbsItems}
      flags={<AdminButton adminUrl={instruction.adminUrl} />}
    >
      <Box display="flex" alignItems="center" gap={1}>
        {instruction.hasExportFile && instruction.exportFileLink && (
          <Button
            variant="outlined"
            startIcon={<GetAppIcon />}
            href={instruction.exportFileLink}
            target="_blank"
            rel="noopener noreferrer"
            data-cy="button-download-export"
          >
            {t('Download Export')}
          </Button>
        )}
        <FollowUpInstructionActions
          instruction={instruction}
          permissions={permissions}
        />
      </Box>
    </PageHeader>
  );
}
