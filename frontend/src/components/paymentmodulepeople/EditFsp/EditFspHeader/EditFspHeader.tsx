import { Box, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';

interface EditFspHeaderProps {
  handleSubmit: () => Promise<void>;
  baseUrl: string;
  permissions: string[];
}

export function EditFspHeader({
  handleSubmit,
  baseUrl,
  permissions,
}: EditFspHeaderProps): React.ReactElement {
  const { t } = useTranslation();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/payment-plans`,
    },
  ];

  return (
    <PageHeader
      title={t('Edit FSP')}
      breadCrumbs={
        hasPermissions(PERMISSIONS.PM_VIEW_LIST, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      <Box display="flex" mt={2} mb={2}>
        <Box mr={3}>
          <Button
            component={Link}
            to={`/${baseUrl}/payment-module/payment-plans`}
          >
            {t('Cancel')}
          </Button>
        </Box>
        <Button variant="contained" color="primary" onClick={handleSubmit}>
          {t('Save')}
        </Button>
      </Box>
    </PageHeader>
  );
}
