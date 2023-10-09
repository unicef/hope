import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useParams } from 'react-router-dom';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { BreadCrumbsItem } from '../../core/BreadCrumbs';
import { PageHeader } from '../../core/PageHeader';
import { getPaymentPlanUrlPart } from '../../../utils/utils';

interface ManagePaymentInstructionsHeaderProps {
  baseUrl: string;
  permissions: string[];
  buttons: ReactElement;
}

export const ManagePaymentInstructionsHeader = ({
  baseUrl,
  permissions,
  buttons,
}: ManagePaymentInstructionsHeaderProps): React.ReactElement => {
  const location = useLocation();
  const { t } = useTranslation();
  const { id } = useParams();
  const isFollowUp = location.pathname.indexOf('followup') !== -1;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Program Cycles'),
      to: `/${baseUrl}/payment-module/program-cycles`,
    },
    {
      // TODO add unicef id
      title: t('Payment Plan ID'),
      to: `/${baseUrl}/payment-module/${getPaymentPlanUrlPart(
        isFollowUp,
      )}/${id}`,
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
