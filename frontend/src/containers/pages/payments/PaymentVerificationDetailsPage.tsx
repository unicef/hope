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
  useCashPlanQuery,
  useCashPlanVerificationSamplingChoicesQuery,
} from '../../../__generated__/graphql';
import { VerificationRecordsTable } from '../../tables/payments/VerificationRecordsTable';
import { VerificationRecordsFilters } from '../../tables/payments/VerificationRecordsTable/VerificationRecordsFilters';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';

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

const TableWrapper = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px;
  padding-bottom: 0;
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

  const canCreate =
    hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_CREATE, permissions) &&
    cashPlan.verificationStatus === 'PENDING';

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

        {isFinished && (
          <Button
            variant='contained'
            color='primary'
            component={Link}
            to={`/${businessArea}/grievance-and-feedback/payment-verification/${decodeIdString(
              cashPlan.verifications.edges[0].node.id,
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
        <CashPlanDetailsSection cashPlan={cashPlan} />
      </Container>
      <Container>
        <VerificationPlansSummary cashPlan={cashPlan} />
      </Container>
      {cashPlan.verifications?.edges?.length
        ? cashPlan.verifications.edges.map((edge) => (
            <VerificationPlanDetails
              key={edge.node.id}
              samplingChoicesData={choicesData}
              verificationPlan={edge.node}
              cashPlan={cashPlan}
            />
          ))
        : null}
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
              filter={debouncedFilter}
              id={verificationPlan.id}
              businessArea={businessArea}
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
