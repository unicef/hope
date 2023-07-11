import { Box, Button, Typography } from '@material-ui/core';
import ExpandLessIcon from '@material-ui/icons/ExpandLess';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  PaymentPlanQuery,
  useExportPdfPpSummaryMutation,
} from '../../../../__generated__/graphql';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';
import { usePermissions } from '../../../../hooks/usePermissions';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { LoadingButton } from '../../../core/LoadingButton';
import { Title } from '../../../core/Title';
import { AcceptanceProcessRow } from './AcceptanceProcessRow';

const ButtonContainer = styled(Box)`
  width: 200px;
`;

interface AcceptanceProcessProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const AcceptanceProcess = ({
  paymentPlan,
}: AcceptanceProcessProps): React.ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();
  const { edges } = paymentPlan.approvalProcess;
  const [showAll, setShowAll] = useState(false);
  const [
    mutate,
    { loading: exportPdfLoading },
  ] = useExportPdfPpSummaryMutation();

  const matchDataSize = (
    data: PaymentPlanQuery['paymentPlan']['approvalProcess']['edges'],
  ): PaymentPlanQuery['paymentPlan']['approvalProcess']['edges'] => {
    return showAll ? data : [data[0]];
  };

  if (!edges.length) {
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

  const canExportPdf = hasPermissions(
    PERMISSIONS.PM_EXPORT_PDF_SUMMARY,
    permissions,
  );

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box display='flex' justifyContent='space-between' mt={4}>
          <Title>
            <Typography variant='h6'>{t('Acceptance Process')}</Typography>
          </Title>
          {canExportPdf && (
            <LoadingButton
              loading={exportPdfLoading}
              color='primary'
              variant='contained'
              onClick={handleExportPdf}
            >
              {t('Download Payment Plan Summary')}
            </LoadingButton>
          )}
        </Box>
        {matchDataSize(edges).map((edge) => (
          <AcceptanceProcessRow
            key={edge.node.id}
            acceptanceProcess={edge.node}
            paymentPlan={paymentPlan}
          />
        ))}
        {edges.length > 1 && (
          <ButtonContainer>
            <Button
              variant='outlined'
              color='primary'
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
};
