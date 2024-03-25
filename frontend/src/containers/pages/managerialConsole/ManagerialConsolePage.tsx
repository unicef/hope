import { BaseSection } from '@components/core/BaseSection';
import { PageHeader } from '@components/core/PageHeader';
import { usePermissions } from '@hooks/usePermissions';
import { fetchPaymentPlansManagerial } from '@api/paymentModuleApi';
import { Box } from '@mui/material';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions } from 'src/config/permissions';
import { useQuery } from 'react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';

export const ManagerialConsolePage: React.FC = () => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const canApprove = hasPermissions(
    'PM_ACCEPTANCE_PROCESS_APPROVE',
    permissions,
  );
  const canAuthorize = hasPermissions(
    'PM_ACCEPTANCE_PROCESS_AUTHORIZE',
    permissions,
  );
  const canReview = hasPermissions(
    'PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW',
    permissions,
  );
  const { data, isLoading, isError } = useQuery(
    ['paymentPlans', businessArea],
    () => fetchPaymentPlansManagerial(businessArea),
  );
  console.log(data, isLoading, isError);
  return (
    <>
      <PageHeader title={t('Managerial Console')} />
      {canApprove && (
        <Box mb={6}>
          <BaseSection
            title={t('Payment Plans pending for Approval')}
            buttons={null}
          />
        </Box>
      )}
      {canAuthorize && (
        <Box mb={6}>
          <BaseSection
            title={t('Payment Plans pending for Authorization')}
            buttons={null}
          />
        </Box>
      )}
      {canReview && (
        <Box mb={6}>
          <BaseSection
            title={t('Payment Plans pending for Release')}
            buttons={null}
          />
        </Box>
      )}
      <Box mb={6}>
        <BaseSection
          title={t('Payment Verification Plans Overview')}
          buttons={null}
        />
      </Box>
    </>
  );
};
