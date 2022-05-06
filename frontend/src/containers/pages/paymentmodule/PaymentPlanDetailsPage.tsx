import { Paper } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';

export function PaymentPlanDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const permissions = usePermissions();

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PAYMENT_MODULE_VIEW_LIST, permissions))
    return <PermissionDenied />;

  return (
    <Paper>
      <PageHeader title={t('Payment Plan Details')} />
    </Paper>
  );
}
