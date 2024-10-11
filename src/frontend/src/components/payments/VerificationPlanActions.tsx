import { Box, Button } from '@mui/material';
import { GetApp } from '@mui/icons-material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  CashPlanQuery,
  CashPlanVerificationSamplingChoicesQuery,
  PaymentPlanQuery,
  PaymentVerificationPlanStatus,
  PaymentVerificationPlanVerificationChannel,
  useExportXlsxPaymentVerificationPlanFileMutation,
  useInvalidPaymentVerificationPlanMutation,
} from '@generated/graphql';
import { PERMISSIONS, hasPermissions } from '../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { LoadingButton } from '@core/LoadingButton';
import { Title } from '@core/Title';
import { ActivateVerificationPlan } from './ActivateVerificationPlan';
import { DeleteVerificationPlan } from './DeleteVerificationPlan';
import { DiscardVerificationPlan } from './DiscardVerificationPlan';
import { EditVerificationPlan } from './EditVerificationPlan';
import { FinishVerificationPlan } from './FinishVerificationPlan';
import { ImportXlsx } from './ImportXlsx';

const StyledLink = styled.a`
  text-decoration: none;
`;

interface VerificationPlanActionsProps {
  verificationPlan: PaymentPlanQuery['paymentPlan']['verificationPlans']['edges'][0]['node'];
  samplingChoicesData: CashPlanVerificationSamplingChoicesQuery;
  planNode: CashPlanQuery['cashPlan'] | PaymentPlanQuery['paymentPlan'];
}

export function VerificationPlanActions({
  verificationPlan,
  samplingChoicesData,
  planNode,
}: VerificationPlanActionsProps): React.ReactElement {
  const { t } = useTranslation();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();

  const [mutateExport, { loading: loadingExport }] =
    useExportXlsxPaymentVerificationPlanFileMutation();

  const [mutateInvalid, { loading: loadingInvalid }] =
    useInvalidPaymentVerificationPlanMutation();

  if (!verificationPlan || !samplingChoicesData || !permissions) return null;

  const isPending =
    verificationPlan.status === PaymentVerificationPlanStatus.Pending;
  const isActive =
    verificationPlan.status === PaymentVerificationPlanStatus.Active;

  const verificationChannelXLSX =
    verificationPlan.verificationChannel ===
    PaymentVerificationPlanVerificationChannel.Xlsx;

  const canEdit = hasPermissions(
    PERMISSIONS.PAYMENT_VERIFICATION_UPDATE,
    permissions,
  );
  const canActivate = hasPermissions(
    PERMISSIONS.PAYMENT_VERIFICATION_ACTIVATE,
    permissions,
  );
  const canDelete = hasPermissions(
    PERMISSIONS.PAYMENT_VERIFICATION_DELETE,
    permissions,
  );

  const canFinish = hasPermissions(
    PERMISSIONS.PAYMENT_VERIFICATION_FINISH,
    permissions,
  );
  const canDiscard = hasPermissions(
    PERMISSIONS.PAYMENT_VERIFICATION_DISCARD,
    permissions,
  );
  const canImport = hasPermissions(
    PERMISSIONS.PAYMENT_VERIFICATION_IMPORT,
    permissions,
  );
  const canExport =
    hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_EXPORT, permissions) &&
    !verificationPlan.hasXlsxFile;
  const canDownload =
    hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_EXPORT, permissions) &&
    verificationPlan.hasXlsxFile &&
    !verificationPlan.xlsxFileExporting;
  const canMarkInvalid =
    verificationPlan.xlsxFileWasDownloaded || verificationPlan.xlsxFileImported;

  return (
    <Title>
      <Box display="flex" alignItems="center" justifyContent="flex-end">
        {isPending && (
          <>
            <Box mr={2}>
              {canDelete && (
                <DeleteVerificationPlan
                  cashOrPaymentPlanId={planNode.id}
                  paymentVerificationPlanId={verificationPlan.id}
                />
              )}
            </Box>
            {canEdit && (
              <EditVerificationPlan
                paymentVerificationPlanNode={verificationPlan}
                cashOrPaymentPlanId={planNode.id}
                isPaymentPlan={planNode.__typename === 'PaymentPlanNode'}
              />
            )}
            {canActivate && (
              <Box alignItems="center" display="flex">
                <ActivateVerificationPlan
                  paymentVerificationPlanId={verificationPlan.id}
                />
              </Box>
            )}
          </>
        )}
        {isActive && (
          <Box display="flex">
            {verificationChannelXLSX && (
              <>
                {canExport && (
                  <Box p={2}>
                    <LoadingButton
                      loading={loadingExport}
                      disabled={
                        loadingExport || verificationPlan.xlsxFileExporting
                      }
                      color="primary"
                      variant="outlined"
                      startIcon={<GetApp />}
                      onClick={async () => {
                        try {
                          await mutateExport({
                            variables: {
                              paymentVerificationPlanId: verificationPlan.id,
                            },
                          });
                          showMessage(
                            t(
                              'Exporting XLSX started. Please check your email.',
                            ),
                          );
                        } catch (e) {
                          e.graphQLErrors.map((x) => showMessage(x.message));
                        }
                      }}
                    >
                      {verificationPlan.xlsxFileExporting
                        ? t('Exporting...')
                        : t('Export Xlsx')}
                    </LoadingButton>
                  </Box>
                )}

                {canDownload && (
                  <Box p={2}>
                    <StyledLink
                      download
                      href={`/api/download-payment-verification-plan/${verificationPlan.id}`}
                    >
                      <Button
                        color="primary"
                        variant="outlined"
                        startIcon={<GetApp />}
                      >
                        {t('Download Xlsx')}
                      </Button>
                    </StyledLink>
                  </Box>
                )}

                {canImport && (
                  <Box p={2}>
                    <ImportXlsx
                      paymentVerificationPlanId={verificationPlan.id}
                      cashOrPaymentPlanId={planNode.id}
                    />
                  </Box>
                )}

                {canFinish && verificationPlan.xlsxFileImported && (
                  <FinishVerificationPlan verificationPlan={verificationPlan} />
                )}
                {canDiscard &&
                  !verificationPlan.xlsxFileWasDownloaded &&
                  !verificationPlan.xlsxFileImported && (
                    <DiscardVerificationPlan
                      paymentVerificationPlanId={verificationPlan.id}
                    />
                  )}
                {canMarkInvalid && (
                  <Box p={2}>
                    <LoadingButton
                      loading={loadingInvalid}
                      color="primary"
                      variant="outlined"
                      onClick={async () => {
                        try {
                          await mutateInvalid({
                            variables: {
                              paymentVerificationPlanId: verificationPlan.id,
                            },
                          });
                          showMessage(
                            t('Verification plan marked as invalid.'),
                          );
                        } catch (e) {
                          e.graphQLErrors.map((x) => showMessage(x.message));
                        }
                      }}
                    >
                      {t('Mark as Invalid')}
                    </LoadingButton>
                  </Box>
                )}
              </>
            )}

            {!verificationChannelXLSX && (
              <>
                {canFinish && (
                  <FinishVerificationPlan verificationPlan={verificationPlan} />
                )}
                {canDiscard && (
                  <DiscardVerificationPlan
                    paymentVerificationPlanId={verificationPlan.id}
                  />
                )}
              </>
            )}
          </Box>
        )}
      </Box>
    </Title>
  );
}
