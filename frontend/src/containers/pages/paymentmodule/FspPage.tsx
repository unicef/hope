import { Box } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ContainerColumnWithBorder } from '../../../components/core/ContainerColumnWithBorder';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { FspHeader } from '../../../components/paymentmodule/FspPlanDetails/FspHeader';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';

export const FspPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions))
    return <PermissionDenied />;

  return (
    <>
      <FspHeader businessArea={businessArea} permissions={permissions} />
      <Box m={5}>
        <ContainerColumnWithBorder>FSP display</ContainerColumnWithBorder>
      </Box>
    </>
  );
};
