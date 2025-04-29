import { Box, Button, Typography } from '@mui/material';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  PaymentPlanStatus,
  useExportPdfPpSummaryMutation,
} from '@generated/graphql';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LoadingButton } from '@core/LoadingButton';
import { Title } from '@core/Title';
import { useProgramContext } from '../../../../programContext';
import { AcceptanceProcessRow } from './AcceptanceProcessRow';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

const ButtonContainer = styled(Box)`
  width: 200px;
`;

interface AcceptanceProcessProps {
  paymentPlan: PaymentPlanDetail;
}

function AcceptanceProcess({
  paymentPlan,
}: AcceptanceProcessProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();
  const { isActiveProgram } = useProgramContext();

  const { approvalProcess } = paymentPlan;
  const [showAll, setShowAll] = useState(false);
  const [mutate, { loading: exportPdfLoading }] =
    useExportPdfPpSummaryMutation();

  const matchDataSize = (data) => (showAll ? data : [data[0]]);

  if (!approvalProcess.length) {
    return null;
  }
  const handleExportPdf = async (): Promise<void> => {
    try {
      await mutate({
        variables: {
          paymentPlanId: paymentPlan.id,
        },
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    } finally {
      showMessage(t('PDF generated. Please check your email.'));
    }
  };

  const canExportPdf =
    hasPermissions(PERMISSIONS.PM_EXPORT_PDF_SUMMARY, permissions) &&
    (paymentPlan.status === PaymentPlanStatus.Accepted ||
      paymentPlan.status === PaymentPlanStatus.Finished);

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box display="flex" justifyContent="space-between" mt={4}>
          <Title>
            <Typography variant="h6">{t('Acceptance Process')}</Typography>
          </Title>
          {canExportPdf && (
            <LoadingButton
              loading={exportPdfLoading}
              color="primary"
              variant="contained"
              onClick={handleExportPdf}
              disabled={!isActiveProgram}
            >
              {t('Download Payment Plan Summary')}
            </LoadingButton>
          )}
        </Box>
        {matchDataSize(approvalProcess).map((edge) => (
          <AcceptanceProcessRow
            key={edge.node.id}
            acceptanceProcess={edge.node}
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

export default withErrorBoundary(AcceptanceProcess, 'AcceptanceProcess');
