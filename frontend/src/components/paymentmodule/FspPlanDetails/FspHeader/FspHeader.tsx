import { Box, Button } from '@material-ui/core';
import { Link } from 'react-router-dom';
import EditIcon from '@material-ui/icons/EditRounded';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { PageHeader } from '../../../core/PageHeader';

interface FspHeaderProps {
  businessArea: string;
  permissions: string[];
}

export function FspHeader({
  businessArea,
  permissions,
}: FspHeaderProps): React.ReactElement {
  const { t } = useTranslation();

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
        <Box mr={3}>
          <Button
            color='primary'
            variant='outlined'
            component={Link}
            to={`/${businessArea}/fsp/`}
            startIcon={<EditIcon />}
          >
            {t('Edit')}
          </Button>
        </Box>
      </Box>
    </PageHeader>
  );
}
