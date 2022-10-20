import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BlackLink } from '../../../components/core/BlackLink';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { CashPlanDetailsSection } from '../../../components/payments/CashPlanDetailsSection';
import { CreateVerificationPlan } from '../../../components/payments/CreateVerificationPlan';
import { VerificationPlanDetails } from '../../../components/payments/VerificationPlanDetails';
import { VerificationPlansSummary } from '../../../components/payments/VerificationPlansSummary';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { decodeIdString, isPermissionDeniedError } from '../../../utils/utils';
import {
  CashPlanNode,
  PaymentVerificationPlanStatus,
  useCashPlanQuery,
  useCashPlanVerificationSamplingChoicesQuery,
} from '../../../__generated__/graphql';
import { VerificationRecordsTable } from '../../tables/payments/VerificationRecordsTable';
import { VerificationRecordsFilters } from '../../tables/payments/VerificationRecordsTable/VerificationRecordsFilters';
import { UniversalActivityLogTablePaymentVerification } from '../../tables/UniversalActivityLogTablePaymentVerification';

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

export function CashPlanVerificationDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const permissions = usePermissions();
  const businessArea = useBusinessArea();
  const [filter, setFilter] = useState({
    search: null,
    status: null,
    verificationChannel: null,
    cashPlanPaymentVerification: null,
  });
  const debouncedFilter = useDebounce(filter, 500);
  const { id } = useParams();
  const { data, loading, error } = useCashPlanQuery({
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

  const cashPlan= data.cashPlan as CashPlanNode;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Payment Verification',
      to: `/${businessArea}/payment-verification`,
    },
  ];

  const canCreate = hasPermissions(
    PERMISSIONS.PAYMENT_VERIFICATION_CREATE,
    permissions,
  );

  const statesArray = cashPlan.verificationPlans?.edges?.map((v) => v.node.status);

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
    cashPlan?.paymentVerificationSummary?.status === 'FINISHED';

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
          <CreateVerificationPlan
            disabled={false}
            cashPlanId={cashPlan.id}
            canCreatePaymentVerificationPlan={
              cashPlan.canCreatePaymentVerificationPlan
            }
          />
        )}

        {isFinished && (
          <Button
            variant='contained'
            color='primary'
            component={Link}
            to={`/${businessArea}/grievance-and-feedback/payment-verification/${decodeIdString(
              cashPlan.id,
            )}`}
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
        <CashPlanDetailsSection planNode={cashPlan} />
      </Container>
      <Container>
        <VerificationPlansSummary planNode={cashPlan} />
      </Container>
      {cashPlan.verificationPlans?.edges?.length
        ? cashPlan.verificationPlans.edges.map((edge) => (
            <VerificationPlanDetails
              key={edge.node.id}
              samplingChoicesData={choicesData}
              verificationPlan={edge.node}
              planNode={cashPlan}
            />
          ))
        : null}
      {canSeeVerificationRecords() ? (
        <>
          <Container>
            <VerificationRecordsFilters
              filter={filter}
              onFilterChange={setFilter}
              verifications={cashPlan.verificationPlans}
            />
          </Container>
          <TableWrapper>
            <VerificationRecordsTable
              filter={debouncedFilter}
              cashPlanId={cashPlan.id}
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
      {cashPlan.verificationPlans?.edges[0]?.node?.id &&
        hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
          <UniversalActivityLogTablePaymentVerification
            objectId={cashPlan.id}
          />
        )}
    </>
  );
}
