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
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { LoadingButton } from '@core/LoadingButton';
import { Title } from '@core/Title';
import { ActivateVerificationPlan } from './ActivateVerificationPlan';
import { DeleteVerificationPlan } from './DeleteVerificationPlan';
import { DiscardVerificationPlan } from './DiscardVerificationPlan';
import { EditVerificationPlan } from './EditVerificationPlan';
import { FinishVerificationPlan } from './FinishVerificationPlan';
import { ImportXlsx } from './ImportXlsx';
import type { ReactElement } from 'react';
import { useEffect, useRef } from 'react';
import type { PaymentVerificationPlanDetails } from '@restgenerated/models/PaymentVerificationPlanDetails';
import { showApiErrorMessages } from '@utils/utils';
import { restQueryKey } from '@utils/queryKeys';

const StyledLink = styled.a`
  text-decoration: none;
`;

interface VerificationPlanActionsProps {
  verificationPlan: PaymentVerificationPlanDetails['paymentVerificationPlans'][number];
  paymentPlanNode: PaymentVerificationPlanDetails;
}

export function VerificationPlanActions({
  verificationPlan,
  paymentPlanNode,
}: VerificationPlanActionsProps): ReactElement {
  const { t } = useTranslation();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const { businessArea, programCode } = useBaseUrl();
  const queryClient = useQueryClient();
  const pollingIntervalRef = useRef(null);

  const exportXlsxMutation = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsExportXlsxCreate(
        {
          businessAreaSlug: businessArea,
          id: paymentPlanNode.id,
          programCode: programCode,
          verificationPlanId: verificationPlan.id,
        },
      ),
    onSuccess: () => {
      // Start polling to check when export is complete
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }

      pollingIntervalRef.current = setInterval(() => {
        queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsPaymentVerificationsRetrieve,
          ),
        });
      }, 2000);
    },
  });

  // Stop polling when file is ready or component unmounts
  useEffect(() => {
    if (!verificationPlan.xlsxFileExporting && pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [verificationPlan.xlsxFileExporting]);

  const invalidVerificationPlanMutation = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsInvalidVerificationPlanCreate(
        {
          businessAreaSlug: businessArea,
          id: paymentPlanNode.id,
          programCode: programCode,
          verificationPlanId: verificationPlan.id,
        },
      ),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentVerificationsRetrieve,
        ),
      });
    },
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
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
        }}
      >
        {isPending && (
          <>
            <Box
              sx={{
                mr: 2,
              }}
            >
              {canDelete && (
                <DeleteVerificationPlan
                  paymentPlanId={paymentPlanNode.id}
                  paymentVerificationPlanId={verificationPlan.id}
                />
              )}
            </Box>
            {canEdit && (
              <EditVerificationPlan
                paymentVerificationPlanNode={verificationPlan}
                paymentPlanId={paymentPlanNode.id}
              />
            )}
            {canActivate && (
              <Box
                sx={{
                  alignItems: 'center',
                  display: 'flex',
                }}
              >
                <ActivateVerificationPlan
                  paymentVerificationPlanId={verificationPlan.id}
                  paymentPlanId={paymentPlanNode.id}
                />
              </Box>
            )}
          </>
        )}
        {isActive && (
          <Box
            sx={{
              display: 'flex',
            }}
          >
            {verificationChannelXLSX && (
              <>
                {canExport && (
                  <Box
                    sx={{
                      p: 2,
                    }}
                  >
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
                  <Box
                    sx={{
                      p: 2,
                    }}
                  >
                    <StyledLink
                      download
                      href={`/api/download-payment-verification-plan/${verificationPlan.id}`}
                      onClick={() => {
                        setTimeout(() => {
                          queryClient.invalidateQueries({
                            queryKey: restQueryKey(
                              RestService.restBusinessAreasProgramsPaymentVerificationsRetrieve,
                            ),
                          });
                        }, 1000);
                      }}
                    >
                      <Button
                        color="primary"
                        variant="outlined"
                        data-cy="download-xlsx"
                        startIcon={<GetApp />}
                        data-perm={PERMISSIONS.PAYMENT_VERIFICATION_EXPORT}
                      >
                        {t('Download Xlsx')}
                      </Button>
                    </StyledLink>
                  </Box>
                )}

                {canImport && (
                  <Box
                    data-cy="import-xlsx"
                    sx={{
                      p: 2,
                    }}
                  >
                    <ImportXlsx
                      paymentVerificationPlanId={verificationPlan.id}
                      paymentPlanId={paymentPlanNode.id}
                    />
                  </Box>
                )}

                {canFinish && verificationPlan.xlsxFileImported && (
                  <FinishVerificationPlan
                    verificationPlan={verificationPlan}
                    paymentPlanId={paymentPlanNode.id}
                  />
                )}
                {canDiscard &&
                  !verificationPlan.xlsxFileWasDownloaded &&
                  !verificationPlan.xlsxFileImported && (
                    <DiscardVerificationPlan
                      paymentVerificationPlanId={verificationPlan.id}
                      paymentPlanId={paymentPlanNode.id}
                    />
                  )}
                {canMarkInvalid && (
                  <Box
                    sx={{
                      p: 2,
                    }}
                  >
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
                    paymentPlanId={paymentPlanNode.id}
                  />
                )}
                {canDiscard && (
                  <DiscardVerificationPlan
                    paymentVerificationPlanId={verificationPlan.id}
                    paymentPlanId={paymentPlanNode.id}
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
