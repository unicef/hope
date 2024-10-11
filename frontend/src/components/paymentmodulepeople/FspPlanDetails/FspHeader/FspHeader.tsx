import { Box, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import EditIcon from '@mui/icons-material/EditRounded';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';

interface FspHeaderProps {
  baseUrl: string;
  permissions: string[];
}

export function FspHeader({
  baseUrl,
  permissions,
}: FspHeaderProps): React.ReactElement {
  const { t } = useTranslation();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/payment-plans`,
    },
  ];

  return (
    <PageHeader
      title={t('Set up FSP')}
      breadCrumbs={
        hasPermissions(PERMISSIONS.PM_VIEW_LIST, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      <Box display="flex" mt={2} mb={2}>
        <Box mr={3}>
          <Button
            color="primary"
            variant="outlined"
            component={Link}
            to={`/${baseUrl}/fsp/`}
            startIcon={<EditIcon />}
          >
            {t('Edit')}
          </Button>
        </Box>
      </Box>
    </PageHeader>
  );
}
