import { Box, Button } from '@material-ui/core';
import { Link } from 'react-router-dom';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { PageHeader } from '../../../core/PageHeader';
import { LoadingButton } from '../../../core/LoadingButton';

interface CreatePaymentPlanHeaderProps {
  handleSubmit: () => Promise<void>;
  businessArea: string;
  permissions: string[];
  loadingCreate: boolean;
}

export const CreatePaymentPlanHeader = ({
  handleSubmit,
  businessArea,
  permissions,
  loadingCreate,
}: CreatePaymentPlanHeaderProps): React.ReactElement => {
  const { t } = useTranslation();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${businessArea}/payment-module/`,
    },
  ];

  return (
    <PageHeader
      title={t('New Payment Plan')}
      breadCrumbs={
        hasPermissions(PERMISSIONS.PAYMENT_MODULE_VIEW_LIST, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      <Box display='flex' mt={2} mb={2}>
        <Box mr={3}>
          <Button component={Link} to={`/${businessArea}/payment-module`}>
            {t('Cancel')}
          </Button>
        </Box>
        <LoadingButton
          loading={loadingCreate}
          variant='contained'
          color='primary'
          onClick={handleSubmit}
        >
          {t('Save')}
        </LoadingButton>
      </Box>
    </PageHeader>
  );
};
