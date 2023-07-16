import { Box, Button, Grid, Typography } from '@material-ui/core';
import { GetApp } from '@material-ui/icons';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { usePermissions } from '../../hooks/usePermissions';
import { useSnackbar } from '../../hooks/useSnackBar';
import {
  choicesToDict,
  paymentVerificationStatusToColor,
} from '../../utils/utils';
import {
  CashPlanQuery,
  CashPlanVerificationSamplingChoicesQuery,
  PaymentPlanQuery,
  PaymentVerificationPlanStatus,
  PaymentVerificationPlanVerificationChannel,
  useExportXlsxPaymentVerificationPlanFileMutation,
  useInvalidPaymentVerificationPlanMutation,
} from '../../__generated__/graphql';
import { LabelizedField } from '../core/LabelizedField';
import { LoadingButton } from '../core/LoadingButton';
import { StatusBox } from '../core/StatusBox';
import { Title } from '../core/Title';
import { UniversalMoment } from '../core/UniversalMoment';
import { ActivateVerificationPlan } from './ActivateVerificationPlan';
import { DeleteVerificationPlan } from './DeleteVerificationPlan';
import { DiscardVerificationPlan } from './DiscardVerificationPlan';
import { EditVerificationPlan } from './EditVerificationPlan';
import { FinishVerificationPlan } from './FinishVerificationPlan';
import { ImportXlsx } from './ImportXlsx';
import { VerificationPlanDetailsChart } from './VerificationPlanChart';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: column;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;
`;

const StyledLink = styled.a`
  text-decoration: none;
`;

const StyledBox = styled(Box)`
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
`;

interface VerificationPlanDetailsProps {
  verificationPlan: PaymentPlanQuery['paymentPlan']['verificationPlans']['edges'][0]['node'];
  samplingChoicesData: CashPlanVerificationSamplingChoicesQuery;
  planNode: CashPlanQuery['cashPlan'] | PaymentPlanQuery['paymentPlan'];
}

export const VerificationPlanDetails = ({
  verificationPlan,
  samplingChoicesData,
  planNode,
}: VerificationPlanDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();

  const [
    mutateExport,
    { loading: loadingExport },
  ] = useExportXlsxPaymentVerificationPlanFileMutation();

  const [
    mutateInvalid,
    { loading: loadingInvalid },
  ] = useInvalidPaymentVerificationPlanMutation();

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

  const samplingChoicesDict = choicesToDict(
    samplingChoicesData.cashPlanVerificationSamplingChoices,
  );
  return (
    <Container>
      <Grid container>
        <Grid item xs={6}>
          <Title>
            <Typography variant='h6'>
              {t('Verification Plan')} #{verificationPlan.unicefId}
            </Typography>
          </Title>
        </Grid>
        <Grid item xs={6}>
          <StyledBox>
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
                  <Box alignItems='center' display='flex'>
                    <ActivateVerificationPlan
                      paymentVerificationPlanId={verificationPlan.id}
                    />
                  </Box>
                )}
              </>
            )}
            {isActive && (
              <Box display='flex'>
                {verificationChannelXLSX && (
                  <>
                    {canExport && (
                      <Box p={2}>
                        <LoadingButton
                          loading={loadingExport}
                          disabled={
                            loadingExport || verificationPlan.xlsxFileExporting
                          }
                          color='primary'
                          variant='outlined'
                          startIcon={<GetApp />}
                          onClick={async () => {
                            try {
                              await mutateExport({
                                variables: {
                                  paymentVerificationPlanId:
                                    verificationPlan.id,
                                },
                              });
                              showMessage(
                                t(
                                  'Exporting XLSX started. Please check your email.',
                                ),
                              );
                            } catch (e) {
                              e.graphQLErrors.map((x) =>
                                showMessage(x.message),
                              );
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
                            color='primary'
                            variant='outlined'
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
                      <FinishVerificationPlan
                        verificationPlan={verificationPlan}
                      />
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
                          color='primary'
                          variant='outlined'
                          onClick={async () => {
                            try {
                              await mutateInvalid({
                                variables: {
                                  paymentVerificationPlanId:
                                    verificationPlan.id,
                                },
                              });
                              showMessage(
                                t('Verification plan marked as invalid.'),
                              );
                            } catch (e) {
                              e.graphQLErrors.map((x) =>
                                showMessage(x.message),
                              );
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
                      />
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
          </StyledBox>
        </Grid>
      </Grid>
      <Grid container>
        <Grid item xs={11}>
          <Grid container>
            <Grid item xs={3}>
              <LabelizedField label={t('STATUS')}>
                <StatusBox
                  status={verificationPlan.status}
                  statusToColor={paymentVerificationStatusToColor}
                  dataCy='verification-plan-status'
                />
              </LabelizedField>
            </Grid>
            {[
              {
                label: t('SAMPLING'),
                value: samplingChoicesDict[verificationPlan.sampling],
              },
              {
                label: t('RESPONDED'),
                value: verificationPlan.respondedCount,
              },
              {
                label: t('RECEIVED WITH ISSUES'),
                value: verificationPlan.receivedWithProblemsCount,
              },
              {
                label: t('VERIFICATION CHANNEL'),
                value: verificationPlan.verificationChannel,
              },
              {
                label: t('SAMPLE SIZE'),
                value: verificationPlan.sampleSize,
              },
              {
                label: t('RECEIVED'),
                value: verificationPlan.receivedCount,
              },
              {
                label: t('NOT RECEIVED'),
                value: verificationPlan.notReceivedCount,
              },
              {
                label: t('ACTIVATION DATE'),
                value: (
                  <UniversalMoment>
                    {verificationPlan.activationDate}
                  </UniversalMoment>
                ),
              },
              {
                label: t('COMPLETION DATE'),
                value: (
                  <UniversalMoment>
                    {verificationPlan.completionDate}
                  </UniversalMoment>
                ),
              },
            ].map((el) => (
              <Grid item xs={3} key={el.label}>
                <Box pt={2} pb={2}>
                  <LabelizedField label={el.label} value={el.value} />
                </Box>
              </Grid>
            ))}
          </Grid>
        </Grid>
        <Grid item xs={1}>
          <VerificationPlanDetailsChart verificationPlan={verificationPlan} />
        </Grid>
      </Grid>
    </Container>
  );
};
