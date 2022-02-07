import { Box, Grid, Typography } from '@material-ui/core';
import DeleteIcon from '@material-ui/icons/Delete';
import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { usePermissions } from '../../hooks/usePermissions';
import {
  choicesToDict,
  paymentVerificationStatusToColor,
} from '../../utils/utils';
import {
  CashPlanQuery,
  CashPlanVerificationSamplingChoicesQuery,
} from '../../__generated__/graphql';
import { ErrorButton } from '../core/ErrorButton';
import { LabelizedField } from '../core/LabelizedField';
import { StatusBox } from '../core/StatusBox';
import { UniversalMoment } from '../core/UniversalMoment';
import { EditVerificationPlan } from './EditVerificationPlan';

interface VerificationPlanDetailsProps {
  verificationPlan: CashPlanQuery['cashPlan']['verifications']['edges'][number]['node'];
  samplingChoicesData: CashPlanVerificationSamplingChoicesQuery;
  cashPlan: CashPlanQuery['cashPlan'];
}

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

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

const ChartContainer = styled.div`
  width: 150px;
  height: 150px;
`;

export const VerificationPlanDetails = ({
  verificationPlan,
  samplingChoicesData,
  cashPlan,
}: VerificationPlanDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  const permissions = usePermissions();
  if (!verificationPlan || !samplingChoicesData || !permissions) return null;

  const canEditAndActivate =
    cashPlan.verificationStatus === 'PENDING' &&
    cashPlan.verifications?.edges?.length !== 0;
  const canEdit =
    hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_UPDATE, permissions) &&
    canEditAndActivate;
  const samplingChoicesDict = choicesToDict(
    samplingChoicesData.cashPlanVerificationSamplingChoices,
  );

  const handleDelete = (): void => {
    console.log('DELETE VERIFICATION PLAN');
  };

  return (
    <Container>
      <Box display='flex' justifyContent='space-between'>
        <Title>
          <Typography variant='h6'>{t('Verification Plan Details')}</Typography>
        </Title>
        <Box display='flex' alignItems='center'>
          <Box mr={2}>
            <ErrorButton
              onClick={() => handleDelete()}
              startIcon={<DeleteIcon />}
            >
              {t('Delete')}
            </ErrorButton>
          </Box>
          {canEdit && (
            <EditVerificationPlan
              cashPlanId={cashPlan.id}
              cashPlanVerificationId={cashPlan.verifications.edges[0].node.id}
            />
          )}
        </Box>
      </Box>

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
  );
};
