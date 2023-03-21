import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { PageHeader } from '../../../core/PageHeader';

interface EditFspHeaderProps {
  businessArea: string;
  permissions: string[];
}

export const EditSetUpFspHeader = ({
  businessArea,
  permissions,
}: EditFspHeaderProps): React.ReactElement => {
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
      title={t('Edit Set up FSP')}
      breadCrumbs={
        hasPermissions(
          PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP,
          permissions,
        )
          ? breadCrumbsItems
          : null
      }
    />
  );
};
