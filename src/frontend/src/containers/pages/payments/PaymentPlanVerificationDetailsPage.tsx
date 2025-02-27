import { BlackLink } from '@components/core/BlackLink';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TableWrapper } from '@components/core/TableWrapper';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { CashPlanDetailsSection } from '@components/payments/CashPlanDetailsSection';
import { CreateVerificationPlan } from '@components/payments/CreateVerificationPlan';
import { VerificationPlanDetails } from '@components/payments/VerificationPlanDetails';
import { VerificationPlansSummary } from '@components/payments/VerificationPlansSummary';
import { PeopleVerificationsTable } from '@containers/tables/payments/VerificationRecordsTable/People/PeopleVerificationsTable';
import {
  PaymentVerificationPlanStatus,
  useCashPlanVerificationSamplingChoicesQuery,
  usePaymentPlanQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Button } from '@mui/material';
import {
  decodeIdString,
  getFilterFromQueryParams,
  isPermissionDeniedError,
} from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import styled from 'styled-components';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useProgramContext } from '../../../programContext';
import { UniversalActivityLogTablePaymentVerification } from '../../tables/UniversalActivityLogTablePaymentVerification';
import { VerificationsTable } from '../../tables/payments/VerificationRecordsTable';
import { VerificationRecordsFilters } from '../../tables/payments/VerificationRecordsTable/VerificationRecordsFilters';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: 32px 44px;
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

const initialFilter = {
  search: '',
  status: '',
  verificationChannel: '',
  paymentVerificationPlan: '',
};

function PaymentPlanVerificationDetailsPage(): ReactElement {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const permissions = usePermissions();
  const { baseUrl, businessArea, isAllPrograms } = useBaseUrl();
  const location = useLocation();
  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const { paymentPlanId } = useParams();
  const { data, loading, error } = usePaymentPlanQuery({
    variables: { id: paymentPlanId },
    fetchPolicy: 'cache-and-network',
  });
  const { data: choicesData, loading: choicesLoading } =
    useCashPlanVerificationSamplingChoicesQuery();
  const { isSocialDctType } = useProgramContext();

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
  const canSeeCreationMessage = (): boolean => statesArray.length === 0;

  const canSeeActivationMessage = (): boolean =>
    !canSeeVerificationRecords() && !canSeeCreationMessage();

  const isFinished =
    paymentPlan?.paymentVerificationSummary?.status === 'FINISHED';

  const { isFollowUp } = paymentPlan;

  const toolbar = (
    <PageHeader
      handleBack={() => navigate(`/${baseUrl}/payment-verification`)}
      title={
        <BlackLink
          data-cy="plan-link"
          to={`/${baseUrl}/payment-module/${
            isFollowUp ? 'followup-payment-plans' : 'payment-plans'
          }/${paymentPlan.id}`}
          fullWidth
        >
          {t('Payment Plan')}{' '}
          <span data-cy="plan-id">{paymentPlan.unicefId}</span>
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
            cashOrPaymentPlanId={paymentPlan.id}
            canCreatePaymentVerificationPlan={
              paymentPlan.canCreatePaymentVerificationPlan
            }
            version={paymentPlan.version}
            isPaymentPlan={true}
          />
        )}

        {isFinished &&
          (isAllPrograms ? (
            <Button
              variant="contained"
              color="primary"
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

  const renderVerificationsTable = () => {
    if (isSocialDctType) {
      return (
        <PeopleVerificationsTable
          paymentPlanId={paymentPlan.id}
          filter={appliedFilter}
          businessArea={businessArea}
          canViewRecordDetails={hasPermissions(
            PERMISSIONS.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
            permissions,
          )}
        />
      );
    }
    return (
      <VerificationsTable
        paymentPlanId={paymentPlan.id}
        filter={appliedFilter}
        businessArea={businessArea}
        canViewRecordDetails={hasPermissions(
          PERMISSIONS.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
          permissions,
        )}
      />
    );
  };

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
          <VerificationRecordsFilters
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            verifications={paymentPlan.verificationPlans}
          />
          <TableWrapper>{renderVerificationsTable()}</TableWrapper>
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
          />
        )}
    </>
  );
}

export default withErrorBoundary(
  PaymentPlanVerificationDetailsPage,
  'PaymentPlanVerificationDetailsPage',
);
