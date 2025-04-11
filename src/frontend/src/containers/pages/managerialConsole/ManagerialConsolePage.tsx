import { bulkActionPaymentPlansManagerial } from '@api/paymentModuleApi';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { ApprovalSection } from '@components/managerialConsole/ApprovalSection';
import { AuthorizationSection } from '@components/managerialConsole/AuthorizationSection';
import { PendingForReleaseSection } from '@components/managerialConsole/PendingForReleaseSection';
import { ReleasedSection } from '@components/managerialConsole/ReleasedSection';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { FC, SetStateAction, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { RestService } from '@restgenerated/services/RestService';
import { PaginatedPaymentPlanList } from '@restgenerated/models/PaginatedPaymentPlanList';

export const ManagerialConsolePage: FC = () => {
  const { t } = useTranslation();
  const { businessAreaSlug } = useBaseUrl();
  const [selectedApproved, setSelectedApproved] = useState([]);
  const [selectedAuthorized, setSelectedAuthorized] = useState([]);
  const [selectedInReview, setSelectedInReview] = useState([]);
  const { showMessage } = useSnackbar();

  const handleSelect = (
    selected: any[],
    setSelected: {
      (value: SetStateAction<any[]>): void;
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
    setSelected: (value: SetStateAction<any[]>) => void,
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
  const fetchPaymentPlans = (status: string) => {
    return RestService.restBusinessAreasPaymentsPaymentPlansManagerialList({
      businessAreaSlug,
      limit: 10000,
      offset: 0,
      //@ts-ignore
      status,
    });
  };

  const {
    data: inApprovalData,
    isLoading: inApprovalLoading,
    refetch: refetchInApproval,
  } = useQuery<PaginatedPaymentPlanList>({
    queryKey: ['paymentPlansInApproval', businessAreaSlug],
    queryFn: () => fetchPaymentPlans('IN_APPROVAL'),
  });

  const {
    data: inAuthorizationData,
    isLoading: inAuthorizationLoading,
    refetch: refetchInAuthorization,
  } = useQuery<PaginatedPaymentPlanList>({
    queryKey: ['paymentPlansInAuthorization', businessAreaSlug],
    queryFn: () => fetchPaymentPlans('IN_AUTHORIZATION'),
  });

  const {
    data: inReviewData,
    isLoading: inReviewLoading,
    refetch: refetchInReview,
  } = useQuery<PaginatedPaymentPlanList>({
    queryKey: ['paymentPlansInReview', businessAreaSlug],
    queryFn: () => fetchPaymentPlans('IN_REVIEW'),
  });

  const {
    data: releasedData,
    isLoading: releasedLoading,
    refetch: refetchReleased,
  } = useQuery<PaginatedPaymentPlanList>({
    queryKey: ['paymentPlansReleased', businessAreaSlug],
    queryFn: () => fetchPaymentPlans('ACCEPTED'),
  });

  const bulkAction = useMutation({
    mutationFn: (params: { ids: string[]; action: string; comment: string }) =>
      bulkActionPaymentPlansManagerial({
        businessAreaSlug,
        ids: params.ids,
        action: params.action,
        comment: params.comment,
      }),
    onSuccess: () => {
      refetchInApproval();
      refetchInAuthorization();
      refetchInReview();
      refetchReleased();
      showMessage(t('Action completed successfully'));
    },
  });

  if (
    inApprovalLoading ||
    inAuthorizationLoading ||
    inReviewLoading ||
    releasedLoading ||
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

  const canSeeReleased = hasPermissions(
    'PAYMENT_VIEW_LIST_MANAGERIAL_RELEASED',
    permissions,
  );

  if (!hasPermissions(PERMISSIONS.PAYMENT_VIEW_LIST_MANAGERIAL, permissions))
    return <PermissionDenied />;

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
          <PendingForReleaseSection
            selectedInReview={selectedInReview}
            setSelectedInReview={setSelectedInReview}
            handleSelect={handleSelect}
            handleSelectAll={handleSelectAll}
            inReviewData={inReviewData}
            bulkAction={bulkAction}
          />
        </Box>
      )}
      {canSeeReleased && <ReleasedSection releasedData={releasedData} />}
    </>
  );
};

export default withErrorBoundary(
  ManagerialConsolePage,
  'ManagerialConsolePage',
);
