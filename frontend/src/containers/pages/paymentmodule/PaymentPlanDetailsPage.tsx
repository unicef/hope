import React from 'react';
import { useParams } from 'react-router-dom';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { AcceptanceProcess } from '../../../components/paymentmodule/PaymentPlanDetails/AcceptanceProcess/AcceptanceProcess';
import { Entitlement } from '../../../components/paymentmodule/PaymentPlanDetails/Entitlement/Entitlement';
import { FspSection } from '../../../components/paymentmodule/PaymentPlanDetails/FspSection';
import { PaymentPlanDetails } from '../../../components/paymentmodule/PaymentPlanDetails/PaymentPlanDetails';
import { PaymentPlanDetailsHeader } from '../../../components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader';
import { PaymentPlanDetailsResults } from '../../../components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { PaymentsTable } from '../../tables/paymentmodule/PaymentsTable';
import {
  PaymentPlanStatus,
  usePaymentPlanQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';

export const PaymentPlanDetailsPage = (): React.ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();
  const businessArea = useBusinessArea();
  const { data, loading } = usePaymentPlanQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });

  if (permissions === null) return null;
  if (!data) return null;
  if (loading) return <LoadingComponent />;
  if (!hasPermissions(PERMISSIONS.PAYMENT_MODULE_VIEW_DETAILS, permissions))
    return <PermissionDenied />;

  const { paymentPlan } = data;
  return (
    <>
      <PaymentPlanDetailsHeader
        paymentPlan={paymentPlan}
        businessArea={businessArea}
        permissions={permissions}
      />
      <PaymentPlanDetails
        businessArea={businessArea}
        paymentPlan={paymentPlan}
      />
      <AcceptanceProcess paymentPlan={paymentPlan} />
      {paymentPlan.status !== PaymentPlanStatus.Open && (
        <>
          <Entitlement paymentPlan={paymentPlan} />
          <FspSection businessArea={businessArea} paymentPlan={paymentPlan} />
        </>
      )}
      <PaymentPlanDetailsResults paymentPlan={paymentPlan} />
      <PaymentsTable
        businessArea={businessArea}
        paymentPlan={paymentPlan}
        canViewDetails
      />
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={paymentPlan.id} />
      )}
    </>
  );
};
