import { Box, Button, Grid, Typography } from '@material-ui/core';
import React, { useState } from 'react';
import { Doughnut } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BlackLink } from '../../components/BlackLink';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { LabelizedField } from '../../components/LabelizedField';
import { LoadingComponent } from '../../components/LoadingComponent';
import { PageHeader } from '../../components/PageHeader';
import { ActivateVerificationPlan } from '../../components/payments/ActivateVerificationPlan';
import { CreateVerificationPlan } from '../../components/payments/CreateVerificationPlan';
import { DiscardVerificationPlan } from '../../components/payments/DiscardVerificationPlan';
import { EditVerificationPlan } from '../../components/payments/EditVerificationPlan';
import { FinishVerificationPlan } from '../../components/payments/FinishVerificationPlan';
import { PermissionDenied } from '../../components/PermissionDenied';
import { StatusBox } from '../../components/StatusBox';
import { UniversalMoment } from '../../components/UniversalMoment';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';
import { usePermissions } from '../../hooks/usePermissions';
import {
  choicesToDict,
  countPercentage,
  isPermissionDeniedError,
  paymentVerificationStatusToColor,
} from '../../utils/utils';
import {
  useCashPlanQuery,
  useCashPlanVerificationSamplingChoicesQuery,
} from '../../__generated__/graphql';
import { UniversalActivityLogTable } from '../tables/UniversalActivityLogTable';
import { VerificationRecordsTable } from '../tables/VerificationRecordsTable';
import { VerificationRecordsFilters } from '../tables/VerificationRecordsTable/VerificationRecordsFilters';

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

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const ChartContainer = styled.div`
  width: 150px;
  height: 150px;
`;

const BorderLeftBox = styled.div`
  padding-left: ${({ theme }) => theme.spacing(6)}px;
  border-left: 1px solid #e0e0e0;
  height: 100%;
`;

const BottomTitle = styled.div`
  color: rgba(0, 0, 0, 0.38);
  font-size: 24px;
  line-height: 28px;
  text-align: center;
  padding: 70px;
`;

const TableWrapper = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px;
  padding-bottom: 0;
`;
const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

export function PaymentVerificationDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const permissions = usePermissions();
  const businessArea = useBusinessArea();
  const [filter, setFilter] = useState({
    search: null,
  });
  const debouncedFilter = useDebounce(filter, 500);
  const { id } = useParams();
  const { data, loading, error } = useCashPlanQuery({
    variables: { id },
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useCashPlanVerificationSamplingChoicesQuery();

  if (loading || choicesLoading) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!data || !choicesData || permissions === null) return null;

  const samplingChoicesDict = choicesToDict(
    choicesData.cashPlanVerificationSamplingChoices,
  );
  const { cashPlan } = data;
  const verificationPlan = cashPlan?.verifications?.edges?.length
    ? cashPlan.verifications.edges[0].node
    : null;
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Payment Verification',
      to: `/${businessArea}/payment-verification`,
    },
  ];
  const bankReconciliationSuccessPercentage = countPercentage(
    cashPlan.bankReconciliationSuccess,
    cashPlan.paymentRecords.totalCount,
  );

  const bankReconciliationErrorPercentage = countPercentage(
    cashPlan.bankReconciliationError,
    cashPlan.paymentRecords.totalCount,
  );

  const canCreate =
    hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_CREATE, permissions) &&
    cashPlan.verificationStatus === 'PENDING' &&
    cashPlan.verifications &&
    cashPlan.verifications.edges.length === 0;

  const canEditAndActivate =
    cashPlan.verificationStatus === 'PENDING' &&
    cashPlan.verifications &&
    cashPlan.verifications.edges.length !== 0;

  const canEdit =
    hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_UPDATE, permissions) &&
    canEditAndActivate;
  const canActivate =
    hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_ACTIVATE, permissions) &&
    canEditAndActivate;

  const canFinishAndDiscard =
    cashPlan.verificationStatus === 'ACTIVE' &&
    cashPlan.verifications &&
    cashPlan.verifications.edges.length !== 0;

  const canFinish =
    hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_FINISH, permissions) &&
    canFinishAndDiscard;
  const canDiscard =
    hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_DISCARD, permissions) &&
    canFinishAndDiscard;

  const isFinished = cashPlan.verificationStatus === 'FINISHED';

  const toolbar = (
    <PageHeader
      title={
        <BlackLink to={`/${businessArea}/cashplans/${cashPlan.id}`}>
          {t('Cash Plan')} {cashPlan.caId}
        </BlackLink>
      }
      breadCrumbs={
        hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      <>
        {canCreate && (
          <CreateVerificationPlan disabled={false} cashPlanId={cashPlan.id} />
        )}
        {(canEdit || canActivate) && (
          <Box alignItems='center' display='flex'>
            {canEdit && (
              <EditVerificationPlan
                cashPlanId={cashPlan.id}
                cashPlanVerificationId={cashPlan.verifications.edges[0].node.id}
              />
            )}
            {canActivate && (
              <ActivateVerificationPlan
                cashPlanVerificationId={cashPlan.verifications.edges[0].node.id}
              />
            )}
          </Box>
        )}
        {(canFinish || canDiscard) && (
          <Box display='flex'>
            {canFinish && (
              <FinishVerificationPlan
                cashPlanVerificationId={cashPlan.verifications.edges[0].node.id}
              />
            )}
            {canDiscard && (
              <DiscardVerificationPlan
                cashPlanVerificationId={cashPlan.verifications.edges[0].node.id}
              />
            )}
          </Box>
        )}
        {isFinished && (
          <Button
            variant='contained'
            color='primary'
            component={Link}
            to={`/${businessArea}/grievance-and-feedback/payment-verification/${cashPlan.id}`}
          >
            {t('View Tickets')}
          </Button>
        )}
      </>
    </PageHeader>
  );

  return (
    <>
      {toolbar}
      <Container>
        <Grid container>
          <Grid item xs={9}>
            <Title>
              <Typography variant='h6'>{t('Cash Plan Details')}</Typography>
            </Title>
            <Grid container>
              {[
                { label: t('PROGRAMME NAME'), value: cashPlan.program.name },
                {
                  label: t('PROGRAMME ID'),
                  value: (
                    <BlackLink
                      to={`/${businessArea}/programs/${cashPlan.program.id}`}
                    >
                      {cashPlan.program?.caId}
                    </BlackLink>
                  ),
                },
                {
                  label: t('PAYMENT RECORDS'),
                  value: cashPlan.paymentRecords.totalCount,
                },
                {
                  label: t('START DATE'),
                  value: (
                    <UniversalMoment>{cashPlan.startDate}</UniversalMoment>
                  ),
                },
                {
                  label: t('END DATE'),
                  value: <UniversalMoment>{cashPlan.endDate}</UniversalMoment>,
                },
              ].map((el) => (
                <Grid item xs={4} key={el.label}>
                  <Box pt={2} pb={2}>
                    <LabelizedField label={el.label}>{el.value}</LabelizedField>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Grid>
          <Grid item xs={3}>
            <BorderLeftBox>
              <Title>
                <Typography variant='h6'>{t('Bank reconciliation')}</Typography>
              </Title>
              <Grid container>
                <Grid item xs={6}>
                  <Grid container direction='column'>
                    <LabelizedField label={t('SUCCESSFUL')}>
                      <p>{bankReconciliationSuccessPercentage}%</p>
                    </LabelizedField>
                    <LabelizedField label={t('ERRONEUS')}>
                      <p>{bankReconciliationErrorPercentage}%</p>
                    </LabelizedField>
                  </Grid>
                </Grid>
                <Grid item xs={6}>
                  <ChartContainer>
                    <Doughnut
                      width={200}
                      height={200}
                      options={{
                        maintainAspectRatio: false,
                        cutoutPercentage: 80,
                        legend: {
                          display: false,
                        },
                      }}
                      data={{
                        labels: [t('SUCCESSFUL'), t('ERRONEUS')],
                        datasets: [
                          {
                            data: [
                              bankReconciliationSuccessPercentage,
                              bankReconciliationErrorPercentage,
                            ],
                            backgroundColor: ['#00509F', '#FFAA1F'],
                            hoverBackgroundColor: ['#00509F', '#FFAA1F'],
                          },
                        ],
                      }}
                    />
                  </ChartContainer>
                </Grid>
              </Grid>
            </BorderLeftBox>
          </Grid>
        </Grid>
      </Container>
      {cashPlan.verifications && cashPlan.verifications.edges.length ? (
        <Container>
          <Title>
            <Typography variant='h6'>
              {t('Verification Plan Details')}
            </Typography>
          </Title>
          <Grid container>
            <Grid item xs={11}>
              <Grid container>
                <Grid item xs={3}>
                  <LabelizedField label={t('STATUS')}>
                    <StatusContainer>
                      <StatusBox
                        status={verificationPlan.status}
                        statusToColor={paymentVerificationStatusToColor}
                      />
                    </StatusContainer>
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
                    label: t('VERIFICATION METHOD'),
                    value: verificationPlan.verificationMethod,
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
              <ChartContainer>
                <Doughnut
                  width={200}
                  height={200}
                  options={{
                    maintainAspectRatio: false,
                    cutoutPercentage: 80,
                    legend: {
                      display: false,
                    },
                  }}
                  data={{
                    labels: [
                      t('RECEIVED'),
                      t('RECEIVED WITH ISSUES'),
                      t('NOT RECEIVED'),
                      t('PENDING'),
                    ],
                    datasets: [
                      {
                        data: [
                          verificationPlan.receivedCount,
                          verificationPlan.receivedWithProblemsCount,
                          verificationPlan.notReceivedCount,
                          verificationPlan.sampleSize -
                            verificationPlan.respondedCount,
                        ],
                        backgroundColor: [
                          '#31D237',
                          '#F57F1A',
                          '#FF0100',
                          '#DCDCDC',
                        ],
                        hoverBackgroundColor: [
                          '#31D237',
                          '#F57F1A',
                          '#FF0100',
                          '#DCDCDC',
                        ],
                      },
                    ],
                  }}
                />
              </ChartContainer>
            </Grid>
          </Grid>
        </Container>
      ) : null}
      {cashPlan.verifications &&
      cashPlan.verifications.edges.length &&
      cashPlan.verificationStatus !== 'PENDING' ? (
        <>
          <Container>
            <VerificationRecordsFilters
              filter={filter}
              onFilterChange={setFilter}
            />
          </Container>
          <Container>
            <VerificationRecordsTable
              verificationMethod={verificationPlan.verificationMethod}
              filter={debouncedFilter}
              id={verificationPlan.id}
              businessArea={businessArea}
              canImport={hasPermissions(
                PERMISSIONS.PAYMENT_VERIFICATION_IMPORT,
                permissions,
              )}
              canExport={hasPermissions(
                PERMISSIONS.PAYMENT_VERIFICATION_EXPORT,
                permissions,
              )}
              canViewRecordDetails={hasPermissions(
                PERMISSIONS.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
                permissions,
              )}
            />
          </Container>
        </>
      ) : null}
      {cashPlan.verifications &&
      cashPlan.verifications.edges.length &&
      cashPlan.verificationStatus !== 'ACTIVE' &&
      cashPlan.verificationStatus !== 'FINISHED' ? (
        <BottomTitle>
          {t('To see more details please activate Verification Plan')}
        </BottomTitle>
      ) : null}
      {!cashPlan.verifications.edges.length &&
      cashPlan.verificationStatus !== 'ACTIVE' ? (
        <BottomTitle>
          {t('To see more details please create Verification Plan')}
        </BottomTitle>
      ) : null}
      {cashPlan.verifications?.edges[0]?.node?.id &&
        hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
          <TableWrapper>
            <UniversalActivityLogTable
              objectId={cashPlan.verifications.edges[0].node.id}
            />
          </TableWrapper>
        )}
    </>
  );
}
