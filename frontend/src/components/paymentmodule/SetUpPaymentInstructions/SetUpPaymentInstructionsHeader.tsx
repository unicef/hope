import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, useLocation } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { BreadCrumbsItem } from '../../core/BreadCrumbs';
import { PageHeader } from '../../core/PageHeader';

interface SetUpPaymentInstructionsHeaderProps {
  baseUrl: string;
  permissions: string[];
  buttons: ReactElement;
}

export const SetUpPaymentInstructionsHeader = ({
  baseUrl,
  permissions,
  buttons,
}: SetUpPaymentInstructionsHeaderProps): React.ReactElement => {
  const location = useLocation();
  const { t } = useTranslation();
  const { id } = useParams();
  const isFollowUp = location.pathname.indexOf('followup') !== -1;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/${
        isFollowUp ? 'followup-payment-plans' : 'payment-plans'
      }/${id}`,
    },
  ];

  return (
    <PageHeader
      title={t('Set up Payment Instruction')}
      breadCrumbs={
        hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      {buttons}
    </PageHeader>
  );
};
