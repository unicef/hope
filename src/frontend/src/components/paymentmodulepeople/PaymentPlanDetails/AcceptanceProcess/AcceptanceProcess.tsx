import { Box, Button, Typography } from '@mui/material';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LoadingButton } from '@core/LoadingButton';
import { Title } from '@core/Title';
import { useProgramContext } from '../../../../programContext';
import { AcceptanceProcessRow } from './AcceptanceProcessRow';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';

const ButtonContainer = styled(Box)`
  width: 200px;
`;

interface AcceptanceProcessProps {
  paymentPlan: PaymentPlanDetail;
}

export function AcceptanceProcess({
  paymentPlan,
}: AcceptanceProcessProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId: programSlug } = useBaseUrl();

  const { approvalProcess } = paymentPlan;
  const [showAll, setShowAll] = useState(false);

  const exportPdfMutation = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansExportPdfPaymentPlanSummaryRetrieve(
        {
          businessAreaSlug: businessArea,
          programSlug: programSlug,
          id: paymentPlan.id,
        },
      ),
  });

  const matchDataSize = (
    data: PaymentPlanDetail['approvalProcess'],
  ): PaymentPlanDetail['approvalProcess'] => (showAll ? data : [data[0]]);

  if (!approvalProcess.length) {
    return null;
  }
  const handleExportPdf = async (): Promise<void> => {
    try {
      await exportPdfMutation.mutateAsync();
      showMessage(t('PDF generated. Please check your email.'));
    } catch (e) {
      showMessage(e.message || t('Failed to export PDF'));
    }
  };

  const canExportPdf =
    hasPermissions(PERMISSIONS.PM_EXPORT_PDF_SUMMARY, permissions) &&
    (paymentPlan.status === PaymentPlanStatusEnum.ACCEPTED ||
      paymentPlan.status === PaymentPlanStatusEnum.FINISHED ||
    paymentPlan.status === PaymentPlanStatusEnum.IN_REVIEW);

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box display="flex" justifyContent="space-between" mt={4}>
          <Title>
            <Typography variant="h6">{t('Acceptance Process')}</Typography>
          </Title>
          {canExportPdf && (
            <LoadingButton
              loading={exportPdfMutation.isPending}
              color="primary"
              variant="contained"
              onClick={handleExportPdf}
              disabled={!isActiveProgram}
            >
              {t('Download Payment Plan Summary')}
            </LoadingButton>
          )}
        </Box>
        {matchDataSize(approvalProcess).map((process, index) => (
          <AcceptanceProcessRow
            key={index}
            acceptanceProcess={process}
            paymentPlan={paymentPlan}
          />
        ))}
        {approvalProcess.length > 1 && (
          <ButtonContainer>
            <Button
              variant="outlined"
              color="primary"
              onClick={() => setShowAll(!showAll)}
              endIcon={showAll ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            >
              {showAll ? t('HIDE') : t('SHOW PREVIOUS')}
            </Button>
          </ButtonContainer>
        )}
      </ContainerColumnWithBorder>
    </Box>
  );
}
