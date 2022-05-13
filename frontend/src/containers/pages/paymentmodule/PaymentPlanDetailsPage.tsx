import React from 'react';
import { useTranslation } from 'react-i18next';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { Entitlement } from '../../../components/paymentmodule/PaymentPlanDetails/Entitlement/Entitlement';
import { PaymentPlanDetails } from '../../../components/paymentmodule/PaymentPlanDetails/PaymentPlanDetails';
import { PaymentPlanDetailsHeader } from '../../../components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader';
import { PaymentPlanDetailsResults } from '../../../components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';

export function PaymentPlanDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const permissions = usePermissions();
  const businessArea = useBusinessArea();

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PAYMENT_MODULE_VIEW_LIST, permissions))
    return <PermissionDenied />;

  return (
    <>
      <PaymentPlanDetailsHeader
        paymentPlan={null}
        businessArea={businessArea}
        permissions={permissions}
      />
      <PaymentPlanDetails
        businessArea={businessArea}
        permissions={permissions}
      />
      <Entitlement businessArea={businessArea} permissions={permissions} />
      <PaymentPlanDetailsResults />
    </>
  );
}
