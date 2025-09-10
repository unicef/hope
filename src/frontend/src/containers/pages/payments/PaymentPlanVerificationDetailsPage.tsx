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
import { PaymentVerificationPlanStatusEnum } from '@restgenerated/models/PaymentVerificationPlanStatusEnum';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Button } from '@mui/material';
import { Choice } from '@restgenerated/models/Choice';
import { PaymentVerificationPlanDetails } from '@restgenerated/models/PaymentVerificationPlanDetails';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
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
  const { paymentPlanId } = useParams();
  const { baseUrl, businessArea, isAllPrograms, programId } = useBaseUrl();
  const location = useLocation();
  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  const {
    data: paymentPlan,
    isLoading,
    error,
  } = useQuery<PaymentVerificationPlanDetails>({
    queryKey: ['PaymentVerificationPlanDetails', businessArea, paymentPlanId, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsRetrieve({
        businessAreaSlug: businessArea,
        id: paymentPlanId,
        programSlug: programId,
      }),
  });

  const { data: choicesData, isLoading: choicesLoading } = useQuery<
    Array<Choice>
  >({
    queryKey: ['samplingChoices', businessArea],
    queryFn: () => RestService.restChoicesPaymentVerificationPlanSamplingList(),
  });

  const { isSocialDctType } = useProgramContext();

  if (isLoading || choicesLoading) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!paymentPlan || !choicesData || permissions === null) return null;

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

  const statesArray = paymentPlan.paymentVerificationPlans?.map(
    (v) => v.status,
  );

  const canSeeVerificationRecords = (): boolean => {
    const showTable =
      statesArray.includes(PaymentVerificationPlanStatusEnum.FINISHED) ||
      statesArray.includes(PaymentVerificationPlanStatusEnum.ACTIVE);

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
      {paymentPlan.paymentVerificationPlans?.length
        ? paymentPlan.paymentVerificationPlans.map((plan) => (
            <VerificationPlanDetails
              key={plan.id}
              verificationPlan={plan}
              paymentPlanNode={paymentPlan}
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
            verifications={paymentPlan.paymentVerificationPlans}
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
      {paymentPlan.paymentVerificationPlans?.[0]?.id &&
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
