import { Box, Button } from '@material-ui/core';
import { Link } from 'react-router-dom';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { PageHeader } from '../../../core/PageHeader';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';

interface EditPaymentPlanHeaderProps {
  handleSubmit: () => Promise<void>;
  businessArea: string;
  permissions: string[];
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const EditPaymentPlanHeader = ({
  handleSubmit,
  businessArea,
  permissions,
  paymentPlan,
}: EditPaymentPlanHeaderProps): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = paymentPlan;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${businessArea}/payment-module/payment-plans/${id}`,
    },
  ];

  return (
    <PageHeader
      title={`${t('Edit Payment Plan')} ID: ${id}`}
      breadCrumbs={
        hasPermissions(PERMISSIONS.PAYMENT_MODULE_VIEW_LIST, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      <Box display='flex' mt={2} mb={2}>
        <Box mr={3}>
          <Button
            component={Link}
            to={`/${businessArea}/payment-module/payment-plans/${id}`}
          >
            {t('Cancel')}
          </Button>
        </Box>
        <Button variant='contained' color='primary' onClick={handleSubmit}>
          {t('Save')}
        </Button>
      </Box>
    </PageHeader>
  );
};
