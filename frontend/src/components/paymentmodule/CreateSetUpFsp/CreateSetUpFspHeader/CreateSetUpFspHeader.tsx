import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { PageHeader } from '../../../core/PageHeader';

interface CreateSetUpFspHeaderProps {
  businessArea: string;
  permissions: string[];
}

export const CreateSetUpFspHeader = ({
  businessArea,
  permissions,
}: CreateSetUpFspHeaderProps): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${businessArea}/payment-module/payment-plans/${id}`,
    },
  ];

  return (
    <PageHeader
      title={t('Set up FSP')}
      breadCrumbs={
        hasPermissions(
          PERMISSIONS.FINANCIAL_SERVICE_PROVIDER_CREATE,
          permissions,
        )
          ? breadCrumbsItems
          : null
      }
    />
  );
};
