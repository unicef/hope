import { Grid, Paper, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { UniversalActivityLogTable } from '../../containers/tables/UniversalActivityLogTable';
import {
  choicesToDict,
  formatCurrencyWithSymbol,
  getPhoneNoLabel,
  paymentStatusToColor,
  verificationRecordsStatusToColor,
} from '../../utils/utils';
import { PaymentQuery } from '../../__generated__/graphql';
import { ContainerColumnWithBorder } from '../core/ContainerColumnWithBorder';
import { LabelizedField } from '../core/LabelizedField';
import { StatusBox } from '../core/StatusBox';
import { UniversalMoment } from '../core/UniversalMoment';
import { Title } from '../core/Title';

const Overview = styled(Paper)`
  margin: 20px;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
`;

interface VerificationPaymentDetailsProps {
  payment: PaymentQuery['payment'];
  canViewActivityLog: boolean;
  choicesData;
}

export function VerificationPaymentDetails({
  payment,
  canViewActivityLog,
  choicesData,
}: VerificationPaymentDetailsProps): React.ReactElement {
  const { t } = useTranslation();
  const deliveryTypeDict = choicesToDict(
    choicesData.paymentRecordDeliveryTypeChoices,
  );

  return (
    <>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>{t('Payment Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label={t('STATUS')}>
              <StatusBox
                status={payment.status}
                statusToColor={paymentStatusToColor}
              />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('TARGET POPULATION')}
              value={payment.targetPopulation.name}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DISTRIBUTION MODALITY')}
              value={payment.distributionModality}
            />
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>{t('Verification Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label={t('STATUS')}>
              <StatusBox
                status={payment.verification.status}
                statusToColor={verificationRecordsStatusToColor}
              />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('AMOUNT RECEIVED')}
              value={formatCurrencyWithSymbol(
                payment.verification.receivedAmount,
                payment.currency,
              )}
            />
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
      <Overview>
        <Title>
          <Typography variant='h6'>{t('Household')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField
              label={t('HOUSEHOLD ID')}
              value={payment.household.unicefId}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('HEAD OF HOUSEHOLD')}
              value={payment.household.headOfHousehold.fullName}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('TOTAL PERSON COVERED')}
              value={payment.household.size}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('PHONE NUMBER')}
              value={getPhoneNoLabel(
                payment.household.headOfHousehold.phoneNo,
                payment.household.headOfHousehold.phoneNoValid,
              )}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('ALT. PHONE NUMBER')}
              value={getPhoneNoLabel(
                payment.household.headOfHousehold.phoneNoAlternative,
                payment.household.headOfHousehold.phoneNoAlternativeValid,
              )}
            />
          </Grid>
        </Grid>
      </Overview>
      <Overview>
        <Title>
          <Typography variant='h6'>{t('Entitlement Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField
              label={t('ENTITLEMENT QUANTITY')}
              value={payment.entitlementQuantity}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DELIVERED QUANTITY')}
              value={payment.deliveredQuantity}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('CURRENCY')} value={payment.currency} />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DELIVERY TYPE')}
              value={deliveryTypeDict[payment.deliveryType]}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DELIVERY DATE')}
              value={<UniversalMoment>{payment.deliveryDate}</UniversalMoment>}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('FSP')}
              value={payment.serviceProvider.fullName}
            />
          </Grid>
        </Grid>
      </Overview>
      {canViewActivityLog && (
        <UniversalActivityLogTable
          objectId={payment.parent.verificationPlans.edges[0].node.id}
        />
      )}
    </>
  );
}
