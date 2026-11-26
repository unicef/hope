import withErrorBoundary from '@components/core/withErrorBoundary';
import AcceptanceProcess from '@components/paymentmodule/PaymentListDetails/AcceptanceProcess/AcceptanceProcess';
import { ConversionToUsd } from '@components/paymentmodule/PaymentListDetails/ConversionToUsd';
import { FspExtraFields } from '@components/paymentmodule/PaymentListDetails/FspExtraFields/FspExtraFields';
import { SupportingDocumentsSection } from '@components/paymentmodule/PaymentListDetails/SupportingDocumentsSection/SupportingDocumentsSection';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingComponent } from '@core/LoadingComponent';
import { OverviewContainer } from '@core/OverviewContainer';
import { PermissionDenied } from '@core/PermissionDenied';
import { TableWrapper } from '@core/TableWrapper';
import { Title } from '@core/Title';
import { BlackLink } from '@core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { PlanTypeEnum } from '@restgenerated/models/PlanTypeEnum';
import { ApiError } from '@restgenerated/core/ApiError';
import { RestService } from '@restgenerated/services/RestService';
import { Grid, Typography } from '@mui/material';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import type { ReactElement } from 'react';
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Navigate, useParams } from 'react-router-dom';
import { PaymentListsTable } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentListsTable';
import { PaymentPlanDetailsHeader } from '@containers/pages/paymentmodule/PaymentPlans/PaymentPlanDetailsHeader';
import FundsCommitmentSection from '@components/paymentmodule/PaymentPlanDetails/FundsCommitment/FundsCommitmentSection';
import { VisionStatusSection } from '@components/paymentmodule/PaymentPlanDetails/VisionStatusSection';
import { UniversalActivityLogTable } from '@containers/tables/UniversalActivityLogTable';
import { ExportPaymentPlanSummaryPdfButton } from './actions/ExportPaymentPlanSummaryPdfButton';
import { LinkedPaymentPlansTable } from './LinkedPaymentPlansTable';
import type { PaymentPlanDetail } from './types';
import {
  isPaymentPlanBackgroundActionBusy,
  planTypeDisplayLabel,
} from './utils';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

const initialFilter = {
  search: '',
  dispersionStartDate: undefined,
  dispersionEndDate: undefined,
  status: [],
  totalEntitledQuantityFrom: null,
  totalEntitledQuantityTo: null,
};

const isVisionReviewActive = (paymentPlan: PaymentPlanDetail | null): boolean =>
  paymentPlan !== null &&
  paymentPlan.status === PaymentPlanStatusEnum.IN_REVIEW &&
  'visionManaged' in paymentPlan &&
  paymentPlan.visionManaged === true;

const PaymentPlanDetailsPage = (): ReactElement => {
  const { paymentPlanId } = useParams<{ paymentPlanId: string }>();
  const { businessArea, programId, baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const [filter] = useState(initialFilter);
  const permissions = usePermissions();
  const queryClient = useQueryClient();
  const {
    data: paymentPlan,
    isLoading,
    error,
  } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentPlansRetrieve,
      {
        businessAreaSlug: businessArea,
        id: paymentPlanId,
        programCode: programId,
      },
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansRetrieve({
        businessAreaSlug: businessArea,
        id: paymentPlanId,
        programCode: programId,
      }),
    enabled: !!paymentPlanId && !!businessArea && !!programId,
    refetchInterval: (query) => {
      const currentPaymentPlan = query.state.data ?? null;
      if (isPaymentPlanBackgroundActionBusy(currentPaymentPlan)) return 3000;
      return isVisionReviewActive(currentPaymentPlan) ? 60000 : false;
    },
    refetchIntervalInBackground: true,
  });

  const wasBusy = useRef(false);
  const wasVisionReviewActive = useRef(false);
  useEffect(() => {
    const isBusy = isPaymentPlanBackgroundActionBusy(paymentPlan ?? null);
    const visionReviewActive = isVisionReviewActive(paymentPlan ?? null);
    if (
      (wasBusy.current && !isBusy) ||
      (wasVisionReviewActive.current && !visionReviewActive)
    ) {
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentListsList,
        ),
      });
    }
    wasBusy.current = isBusy;
    wasVisionReviewActive.current = visionReviewActive;
  }, [paymentPlan, queryClient]);

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_VIEW_DETAIL, permissions))
    return (
      <PermissionDenied permission={PERMISSIONS.PM_PAYMENT_PLAN_VIEW_DETAIL} />
    );
  if (isLoading) return <LoadingComponent />;
  // Payment list links sent before the rename used the payment plan path.
  if (error instanceof ApiError && error.status === 404)
    return (
      <Navigate
        to={`/${baseUrl}/payment-module/payment-lists/${paymentPlanId}`}
        replace
      />
    );

  return (
    <>
      <PaymentPlanDetailsHeader paymentPlan={paymentPlan} />
      <Grid size={{ xs: 12 }}>
        <ContainerColumnWithBorder>
          <Title>
            <Typography variant="h6">{t('Details')}</Typography>
          </Title>
          <OverviewContainer>
            <ResponsiveGridContainer spacing={6}>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Name')}>
                  {paymentPlan?.name ?? '-'}
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Cycle')}>
                  {paymentPlan?.cycle ? (
                    <BlackLink
                      to={`/${baseUrl}/payment-module/program-cycles/${paymentPlan.cycle.id}`}
                    >
                      {paymentPlan.cycle.title}
                    </BlackLink>
                  ) : (
                    '-'
                  )}
                </LabelizedField>
              </ResponsiveGrid>
              {paymentPlan?.planType &&
                paymentPlan.planType !== PlanTypeEnum.REGULAR && (
                  <ResponsiveGrid size="quarter" mobileSize="half">
                    <LabelizedField label={t('Type')}>
                      {t(planTypeDisplayLabel(paymentPlan.planType))}
                    </LabelizedField>
                  </ResponsiveGrid>
                )}
              {paymentPlan?.sourcePaymentPlan && (
                <ResponsiveGrid size="quarter" mobileSize="half">
                  <LabelizedField label={t('Created from')}>
                    <BlackLink
                      to={`/${baseUrl}/payment-module/payment-plans/${paymentPlan.sourcePaymentPlan.id}`}
                      data-cy="source-group-link"
                    >
                      {paymentPlan.sourcePaymentPlan.unicefId ??
                        paymentPlan.sourcePaymentPlan.name}
                    </BlackLink>
                  </LabelizedField>
                </ResponsiveGrid>
              )}
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('FSP')}>
                  {paymentPlan?.financialServiceProvider?.name ?? '-'}
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Currency')}>
                  {paymentPlan?.currency ?? '-'}
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Dispersion Start Date')}>
                  {paymentPlan?.dispersionStartDate ?? '-'}
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Dispersion End Date')}>
                  {paymentPlan?.dispersionEndDate ?? '-'}
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Total Entitled (USD)')}>
                  {paymentPlan?.totalEntitledQuantityUsd ?? '-'}
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Total Delivered (USD)')}>
                  {paymentPlan?.totalDeliveredQuantityUsd ?? '-'}
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Total Undelivered (USD)')}>
                  {paymentPlan?.totalUndeliveredQuantityUsd ?? '-'}
                </LabelizedField>
              </ResponsiveGrid>
            </ResponsiveGridContainer>
          </OverviewContainer>
        </ContainerColumnWithBorder>
      </Grid>
      <AcceptanceProcess
        approvalProcess={paymentPlan?.approvalProcess}
        closure={
          paymentPlan?.status === PaymentPlanStatusEnum.CLOSED
            ? {
                closedBy: paymentPlan.closedBy,
                closedDate: paymentPlan.statusDate,
              }
            : null
        }
        headerAction={
          <ExportPaymentPlanSummaryPdfButton
            paymentPlan={paymentPlan ?? null}
          />
        }
      />
      {paymentPlan?.status === PaymentPlanStatusEnum.LOCKED && (
        <FspExtraFields paymentPlan={paymentPlan} permissions={permissions} />
      )}
      {paymentPlan && (
        <ConversionToUsd
          owner={paymentPlan}
          ownerType="paymentPlan"
          permissions={permissions}
        />
      )}
      {paymentPlan && <VisionStatusSection paymentPlan={paymentPlan} />}
      {paymentPlan &&
        [
          PaymentPlanStatusEnum.IN_REVIEW,
          PaymentPlanStatusEnum.ACCEPTED,
          PaymentPlanStatusEnum.FINISHED,
        ].includes(paymentPlan.status) && (
          <FundsCommitmentSection
            paymentPlan={paymentPlan}
            programCode={programId}
          />
        )}
      {paymentPlan && (
        <SupportingDocumentsSection
          key={paymentPlan.id}
          ownerPath={`payment-plans/${paymentPlan.id}`}
          supportingDocuments={paymentPlan.supportingDocuments}
        />
      )}
      {paymentPlan?.linkedPaymentPlans && (
        <LinkedPaymentPlansTable
          linkedPaymentPlans={paymentPlan.linkedPaymentPlans}
        />
      )}
      <TableWrapper>
        <PaymentListsTable
          filter={filter}
          canViewDetails
          title={t('Payment Lists')}
          paymentPlanId={paymentPlanId}
        />
      </TableWrapper>
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={paymentPlan?.id} />
      )}
    </>
  );
};

export default withErrorBoundary(
  PaymentPlanDetailsPage,
  'PaymentPlanDetailsPage',
);
