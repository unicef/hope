import {
  bulkActionPaymentPlansManagerial,
  fetchPaymentPlansManagerial,
} from '@api/paymentModuleApi';
import { BaseSection } from '@components/core/BaseSection';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { ApprovalSection } from '@components/managerialConsole/ApprovalSection';
import { AuthorizationSection } from '@components/managerialConsole/AuthorizationSection';
import { ReleaseSection } from '@components/managerialConsole/ReleaseSection';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions } from 'src/config/permissions';

export const ManagerialConsolePage: React.FC = () => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const [selectedApproved, setSelectedApproved] = useState([]);
  const [selectedAuthorized, setSelectedAuthorized] = useState([]);
  const [selectedInReview, setSelectedInReview] = useState([]);
  const { showMessage } = useSnackbar();

  const handleSelect = (
    selected: any[],
    setSelected: {
      (value: React.SetStateAction<any[]>): void;
      (arg0: any[]): void;
    },
    id: any,
  ) => {
    if (selected.includes(id)) {
      setSelected(selected.filter((item: any) => item !== id));
    } else {
      setSelected([...selected, id]);
    }
  };

  const handleSelectAll = (
    ids: any[],
    selected: any[],
    setSelected: (value: React.SetStateAction<any[]>) => void,
  ) => {
    let newSelected;
    if (ids.every((id) => selected.includes(id))) {
      newSelected = [];
    } else {
      newSelected = ids;
    }
    setSelected(newSelected);
  };

  const permissions = usePermissions();

  const {
    data: inApprovalData,
    isLoading: inApprovalLoading,
    refetch: refetchInApproval,
  } = useQuery({
    queryKey: ['paymentPlansInApproval', businessArea],
    queryFn: () =>
      fetchPaymentPlansManagerial(businessArea, { status: 'IN_APPROVAL' }),
  });

  const {
    data: inAuthorizationData,
    isLoading: inAuthorizationLoading,
    refetch: refetchInAuthorization,
  } = useQuery({
    queryKey: ['paymentPlansInAuthorization', businessArea],
    queryFn: () =>
      fetchPaymentPlansManagerial(businessArea, {
        status: 'IN_AUTHORIZATION',
      }),
  });

  const {
    data: inReviewData,
    isLoading: inReviewLoading,
    refetch: refetchInReview,
  } = useQuery({
    queryKey: ['paymentPlansInReview', businessArea],
    queryFn: () =>
      fetchPaymentPlansManagerial(businessArea, { status: 'IN_REVIEW' }),
  });

  const bulkAction = useMutation({
    mutationFn: (params: { ids: string[]; action: string; comment: string }) =>
      bulkActionPaymentPlansManagerial(
        businessArea,
        params.ids,
        params.action,
        params.comment,
      ),
    onSuccess: () => {
      refetchInApproval();
      refetchInAuthorization();
      refetchInReview();
      showMessage(t('Action completed successfully'));
    },
  });

  if (
    inApprovalLoading ||
    inAuthorizationLoading ||
    inReviewLoading ||
    !permissions
  ) {
    return <LoadingComponent />;
  }

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

  return (
    <>
      <PageHeader title={t('Managerial Console')} />
      {canApprove && (
        <Box mb={6}>
          {canApprove && (
            <Box mb={6}>
              <ApprovalSection
                selectedApproved={selectedApproved}
                setSelectedApproved={setSelectedApproved}
                handleSelect={handleSelect}
                handleSelectAll={handleSelectAll}
                inApprovalData={inApprovalData}
                bulkAction={bulkAction}
              />
            </Box>
          )}
        </Box>
      )}
      {canAuthorize && (
        <Box mb={6}>
          <AuthorizationSection
            selectedAuthorized={selectedAuthorized}
            setSelectedAuthorized={setSelectedAuthorized}
            handleSelect={handleSelect}
            handleSelectAll={handleSelectAll}
            inAuthorizationData={inAuthorizationData}
            bulkAction={bulkAction}
          />
        </Box>
      )}
      {canReview && (
        <Box mb={6}>
          <ReleaseSection
            selectedInReview={selectedInReview}
            setSelectedInReview={setSelectedInReview}
            handleSelect={handleSelect}
            handleSelectAll={handleSelectAll}
            inReviewData={inReviewData}
            bulkAction={bulkAction}
          />
        </Box>
      )}
    </>
  );
};
