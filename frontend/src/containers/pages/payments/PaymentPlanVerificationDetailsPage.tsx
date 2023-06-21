import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BlackLink } from '../../../components/core/BlackLink';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { CashPlanDetailsSection } from '../../../components/payments/CashPlanDetailsSection';
import { CreateVerificationPlan } from '../../../components/payments/CreateVerificationPlan';
import { VerificationPlanDetails } from '../../../components/payments/VerificationPlanDetails';
import { VerificationPlansSummary } from '../../../components/payments/VerificationPlansSummary';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { decodeIdString, isPermissionDeniedError } from '../../../utils/utils';
import {
  PaymentVerificationPlanStatus,
  useCashPlanVerificationSamplingChoicesQuery,
  usePaymentPlanQuery,
} from '../../../__generated__/graphql';
import { VerificationsTable } from '../../tables/payments/VerificationRecordsTable';
import { VerificationRecordsFilters } from '../../tables/payments/VerificationRecordsTable/VerificationRecordsFilters';
import { UniversalActivityLogTablePaymentVerification } from '../../tables/UniversalActivityLogTablePaymentVerification';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

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

const BottomTitle = styled.div`
  color: rgba(0, 0, 0, 0.38);
  font-size: 24px;
  line-height: 28px;
  text-align: center;
  padding: 70px;
`;

export const PaymentPlanVerificationDetailsPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const permissions = usePermissions();
  const { baseUrl, businessArea, isAllPrograms } = useBaseUrl();
  const [filter, setFilter] = useState({
    search: null,
    status: null,
    verificationChannel: null,
    paymentVerificationPlan: null,
  });
  const debouncedFilter = useDebounce(filter, 500);
  const { id } = useParams();
  const { data, loading, error } = usePaymentPlanQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useCashPlanVerificationSamplingChoicesQuery();

  if (loading || choicesLoading) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!data || !choicesData || permissions === null) return null;

  const { paymentPlan } = data;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Payment Verification',
      to: `/${baseUrl}/payment-verification`,
    },
  ];

  const canCreate = hasPermissions(
    PERMISSIONS.PAYMENT_VERIFICATION_CREATE,
    permissions,
  );

  const statesArray = paymentPlan.verificationPlans?.edges?.map(
    (v) => v.node.status,
  );

  const canSeeVerificationRecords = (): boolean => {
    const showTable =
      statesArray.includes(PaymentVerificationPlanStatus.Finished) ||
      statesArray.includes(PaymentVerificationPlanStatus.Active);

    return showTable && statesArray.length > 0;
  };
  const canSeeCreationMessage = (): boolean => {
    return statesArray.length === 0;
  };

  const canSeeActivationMessage = (): boolean => {
    return !canSeeVerificationRecords() && !canSeeCreationMessage();
  };

  const isFinished =
    paymentPlan?.paymentVerificationSummary?.status === 'FINISHED';

  const toolbar = (
    <PageHeader
      title={
        <BlackLink
          data-cy='plan-link'
          to={`/${baseUrl}/payment-plans/${paymentPlan.id}`}
          fullWidth
        >
          {t('Payment Plan')}{' '}
          <span data-cy='plan-id'>{paymentPlan.unicefId}</span>
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
          <CreateVerificationPlan
            disabled={false}
            cashOrPaymentPlanId={paymentPlan.id}
            canCreatePaymentVerificationPlan={
              paymentPlan.canCreatePaymentVerificationPlan
            }
          />
        )}

        {isFinished &&
          (isAllPrograms ? (
            <Button
              variant='contained'
              color='primary'
              component={Link}
              to={`/${baseUrl}/grievance/payment-verification/${decodeIdString(
                paymentPlan.id,
              )}`}
            >
              {t('View Tickets')}
            </Button>
          ) : null)}
      </>
    </PageHeader>
  );

  return (
    <>
      {toolbar}
      <Container>
        <CashPlanDetailsSection planNode={paymentPlan} />
      </Container>
      <Container>
        <VerificationPlansSummary planNode={paymentPlan} />
      </Container>
      {paymentPlan.verificationPlans?.edges?.length
        ? paymentPlan.verificationPlans.edges.map((edge) => (
            <VerificationPlanDetails
              key={edge.node.id}
              samplingChoicesData={choicesData}
              verificationPlan={edge.node}
              planNode={paymentPlan}
            />
          ))
        : null}
      {canSeeVerificationRecords() ? (
        <>
          <Container>
            <VerificationRecordsFilters
              filter={filter}
              onFilterChange={setFilter}
              verifications={paymentPlan.verificationPlans}
            />
          </Container>
          <TableWrapper>
            <VerificationsTable
              paymentPlanId={paymentPlan.id}
              filter={debouncedFilter}
              businessArea={businessArea}
              canViewRecordDetails={hasPermissions(
                PERMISSIONS.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
                permissions,
              )}
            />
          </TableWrapper>
        </>
      ) : null}
      {canSeeActivationMessage() ? (
        <BottomTitle>
          {t('To see more details please activate Verification Plan')}
        </BottomTitle>
      ) : null}

      {canSeeCreationMessage() ? (
        <BottomTitle>
          {t('To see more details please create Verification Plan')}
        </BottomTitle>
      ) : null}
      {paymentPlan.verificationPlans?.edges[0]?.node?.id &&
        hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
          <UniversalActivityLogTablePaymentVerification
            objectId={paymentPlan.id}
            objectType='PaymentPlan'
          />
        )}
    </>
  );
};
