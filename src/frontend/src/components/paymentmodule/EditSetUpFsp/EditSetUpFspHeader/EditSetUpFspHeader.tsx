import { useTranslation } from 'react-i18next';
import { useParams, useLocation } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';

interface EditFspHeaderProps {
  permissions: string[];
}

export function EditSetUpFspHeader({
  permissions,
}: EditFspHeaderProps): ReactElement {
  const { baseUrl } = useBaseUrl();
  const location = useLocation();
  const { t } = useTranslation();
  const { paymentPlanId } = useParams();
  const isFollowUp = location.pathname.indexOf('followup') !== -1;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/${
        isFollowUp ? 'followup-payment-plans' : 'payment-plans'
      }/${paymentPlanId}`,
    },
  ];
  return (
    <PageHeader
      title={t('Edit Set up FSP')}
      breadCrumbs={
        hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP, permissions)
          ? breadCrumbsItems
          : null
      }
    />
  );
}
