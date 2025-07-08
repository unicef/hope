import { Box, Button } from '@mui/material';
import { GetApp } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentVerificationPlanStatusEnum } from '@restgenerated/models/PaymentVerificationPlanStatusEnum';
import { PERMISSIONS, hasPermissions } from '../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { LoadingButton } from '@core/LoadingButton';
import { Title } from '@core/Title';
import { ActivateVerificationPlan } from './ActivateVerificationPlan';
import { DeleteVerificationPlan } from './DeleteVerificationPlan';
import { DiscardVerificationPlan } from './DiscardVerificationPlan';
import { EditVerificationPlan } from './EditVerificationPlan';
import { FinishVerificationPlan } from './FinishVerificationPlan';
import { ImportXlsx } from './ImportXlsx';
import { ReactElement } from 'react';
import { PaymentVerificationPlanDetails } from '@restgenerated/models/PaymentVerificationPlanDetails';
import { PaymentVerificationPlan } from '@restgenerated/models/PaymentVerificationPlan';
import { showApiErrorMessages } from '@utils/utils';

const StyledLink = styled.a`
  text-decoration: none;
`;

interface VerificationPlanActionsProps {
  verificationPlan: PaymentVerificationPlanDetails['paymentVerificationPlans'][number];
  planNode: PaymentVerificationPlan;
}

export function VerificationPlanActions({
  verificationPlan,
  planNode,
}: VerificationPlanActionsProps): ReactElement {
  const { t } = useTranslation();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const { businessArea, programId: programSlug } = useBaseUrl();

  const exportXlsxMutation = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsExportXlsxCreate(
        {
          businessAreaSlug: businessArea,
          id: planNode.id,
          programSlug: programSlug,
          verificationPlanId: verificationPlan.id,
        },
      ),
  });

  const invalidVerificationPlanMutation = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsInvalidVerificationPlanCreate(
        {
          businessAreaSlug: businessArea,
          id: planNode.id,
          programSlug: programSlug,
          verificationPlanId: verificationPlan.id,
        },
      ),
  });

  if (!verificationPlan || !permissions) return null;

  const isPending =
    verificationPlan.status === PaymentVerificationPlanStatusEnum.PENDING;
  const isActive =
    verificationPlan.status === PaymentVerificationPlanStatusEnum.ACTIVE;

  const verificationChannelXLSX =
    verificationPlan.verificationChannel === 'XLSX';

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
              />
            )}
            {canActivate && (
              <Box alignItems="center" display="flex">
                <ActivateVerificationPlan
                  paymentVerificationPlanId={verificationPlan.id}
                  cashOrPaymentPlanId={planNode.id}
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
                      loading={exportXlsxMutation.isPending}
                      disabled={
                        exportXlsxMutation.isPending ||
                        verificationPlan.xlsxFileExporting
                      }
                      color="primary"
                      variant="outlined"
                      startIcon={<GetApp />}
                      data-cy="export-xlsx"
                      onClick={async () => {
                        try {
                          await exportXlsxMutation.mutateAsync();
                          showMessage(
                            t(
                              'Exporting XLSX started. Please check your email.',
                            ),
                          );
                        } catch (error) {
                          showApiErrorMessages(error, showMessage);
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
                        data-cy="download-xlsx"
                        startIcon={<GetApp />}
                      >
                        {t('Download Xlsx')}
                      </Button>
                    </StyledLink>
                  </Box>
                )}

                {canImport && (
                  <Box p={2} data-cy="import-xlsx">
                    <ImportXlsx
                      paymentVerificationPlanId={verificationPlan.id}
                      cashOrPaymentPlanId={planNode.id}
                    />
                  </Box>
                )}

                {canFinish && verificationPlan.xlsxFileImported && (
                  <FinishVerificationPlan
                    verificationPlan={verificationPlan}
                    cashOrPaymentPlanId={planNode.id}
                  />
                )}
                {canDiscard &&
                  !verificationPlan.xlsxFileWasDownloaded &&
                  !verificationPlan.xlsxFileImported && (
                    <DiscardVerificationPlan
                      paymentVerificationPlanId={verificationPlan.id}
                      cashOrPaymentPlanId={planNode.id}
                    />
                  )}
                {canMarkInvalid && (
                  <Box p={2}>
                    <LoadingButton
                      loading={invalidVerificationPlanMutation.isPending}
                      color="primary"
                      variant="outlined"
                      data-cy="button-mark-as-invalid"
                      onClick={async () => {
                        try {
                          await invalidVerificationPlanMutation.mutateAsync();
                          showMessage(
                            t('Verification plan marked as invalid.'),
                          );
                        } catch (error) {
                          showApiErrorMessages(error, showMessage);
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
                  <FinishVerificationPlan
                    verificationPlan={verificationPlan}
                    cashOrPaymentPlanId={planNode.id}
                  />
                )}
                {canDiscard && (
                  <DiscardVerificationPlan
                    paymentVerificationPlanId={verificationPlan.id}
                    cashOrPaymentPlanId={planNode.id}
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
