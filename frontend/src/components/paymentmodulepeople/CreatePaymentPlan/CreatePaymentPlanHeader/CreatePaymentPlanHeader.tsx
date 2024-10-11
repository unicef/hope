import { Box, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { LoadingButton } from '@core/LoadingButton';

interface CreatePaymentPlanHeaderProps {
  handleSubmit: () => Promise<void>;
  baseUrl: string;
  permissions: string[];
  loadingCreate: boolean;
}

export function CreatePaymentPlanHeader({
  handleSubmit,
  baseUrl,
  permissions,
  loadingCreate,
}: CreatePaymentPlanHeaderProps): React.ReactElement {
  const { t } = useTranslation();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/payment-plans`,
    },
  ];

  return (
    <PageHeader
      title={t('New Payment Plan')}
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
        <LoadingButton
          loading={loadingCreate}
          variant="contained"
          color="primary"
          onClick={handleSubmit}
          data-cy="button-save-payment-plan"
        >
          {t('Save')}
        </LoadingButton>
      </Box>
    </PageHeader>
  );
}
