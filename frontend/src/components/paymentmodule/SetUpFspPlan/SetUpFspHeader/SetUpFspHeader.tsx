import { Box, Button } from '@material-ui/core';
import { Link, useParams } from 'react-router-dom';
import EditIcon from '@material-ui/icons/EditRounded';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { PageHeader } from '../../../core/PageHeader';

interface SetUpFspHeaderProps {
  businessArea: string;
  permissions: string[];
}

export function SetUpFspHeader({
  businessArea,
  permissions,
}: SetUpFspHeaderProps): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${businessArea}/payment-module/`,
    },
  ];

  return (
    <PageHeader
      title={t('Set up FSP')}
      breadCrumbs={
        hasPermissions(PERMISSIONS.PAYMENT_MODULE_VIEW_LIST, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      <Box display='flex' mt={2} mb={2}>
        <Button
          color='primary'
          variant='outlined'
          component={Link}
          to={`/${businessArea}/payment-module/payment-plans/${id}/setup-fsp/edit`}
          startIcon={<EditIcon />}
        >
          {t('Edit')}
        </Button>
      </Box>
    </PageHeader>
  );
}
