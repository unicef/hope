import React from 'react';
import { ContainerColumnWithBorder } from '../../../components/core/ContainerColumnWithBorder';
import { Missing } from '../../../components/core/Missing';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { SetUpPaymentInstructionsHeader } from '../../../components/paymentmodule/SetUpPaymentInstructions/SetUpPaymentInstructionsHeader';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';

export const SetUpPaymentInstructionsPage = (): React.ReactElement => {
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_SET_UP_PAYMENT_INSTRUCTIONS, permissions))
    return <PermissionDenied />;

  return (
    <>
      <SetUpPaymentInstructionsHeader
        baseUrl={baseUrl}
        permissions={permissions}
      />
      <ContainerColumnWithBorder>
        <Missing />
      </ContainerColumnWithBorder>
    </>
  );
};
