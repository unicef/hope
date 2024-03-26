import { BaseSection } from '@components/core/BaseSection';
import { PageHeader } from '@components/core/PageHeader';
import { usePermissions } from '@hooks/usePermissions';
import {
  bulkActionPaymentPlansManagerial,
  fetchPaymentPlansManagerial,
} from '@api/paymentModuleApi';
import {
  Box,
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@mui/material';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions } from 'src/config/permissions';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { ApprovePaymentPlansModal } from '@components/managerialConsole/ApprovePaymentPlansModal';
import { AuthorizePaymentPlansModal } from '@components/managerialConsole/AuthorizePaymentPlansModal';
import { ReleasePaymentPlansModal } from '@components/managerialConsole/ReleasePaymentPlansModal';

export const ManagerialConsolePage: React.FC = () => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const [selectedApproved, setSelectedApproved] = useState([]);
  const [selectedAuthorized, setSelectedAuthorized] = useState([]);
  const [selectedInReview, setSelectedInReview] = useState([]);

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

  const { data: inApprovalData, isLoading: inApprovalLoading } = useQuery({
    queryKey: ['paymentPlansInApproval', businessArea],
    queryFn: () =>
      fetchPaymentPlansManagerial(businessArea, { status: 'IN_APPROVAL' }),
  });

  const { data: inAuthorizationData, isLoading: inAuthorizationLoading } =
    useQuery({
      queryKey: ['paymentPlansInAuthorization', businessArea],
      queryFn: () =>
        fetchPaymentPlansManagerial(businessArea, {
          status: 'IN_AUTHORIZATION',
        }),
    });

  const { data: inReviewData, isLoading: inReviewLoading } = useQuery({
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
  });

  if (inApprovalLoading || inAuthorizationLoading || inReviewLoading) {
    return <LoadingComponent />;
  }

  return (
    <>
      <PageHeader title={t('Managerial Console')} />
      {canApprove && (
        <Box mb={6}>
          <BaseSection
            title={t('Payment Plans pending for Approval')}
            buttons={
              <ApprovePaymentPlansModal
                selectedPlans={selectedApproved}
                onApprove={() =>
                  bulkAction.mutateAsync({
                    ids: selectedApproved,
                    action: 'APPROVE',
                    comment: 'Approved',
                  })
                }
              />
            }
          >
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox />
                  </TableCell>
                  <TableCell>{t('Payment Plan ID')}</TableCell>
                  <TableCell>{t('Status')}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {inApprovalData.results?.map((plan) => (
                  <TableRow key={plan.unicef_id}>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedApproved.includes(plan.unicef_id)}
                        onChange={() =>
                          handleSelect(
                            selectedApproved,
                            setSelectedApproved,
                            plan.unicef_id,
                          )
                        }
                      />
                    </TableCell>
                    <TableCell>{plan.unicef_id}</TableCell>
                    <TableCell>{plan.status}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </BaseSection>
        </Box>
      )}
      {canAuthorize && (
        <Box mb={6}>
          <BaseSection
            title={t('Payment Plans pending for Authorization')}
            buttons={
              <AuthorizePaymentPlansModal
                selectedPlans={selectedAuthorized}
                onAuthorize={() =>
                  bulkAction.mutateAsync({
                    ids: selectedAuthorized,
                    action: 'AUTHORIZE',
                    comment: 'Authorized',
                  })
                }
              />
            }
          >
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox />
                  </TableCell>
                  <TableCell>{t('Payment Plan ID')}</TableCell>
                  <TableCell>{t('Status')}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {inAuthorizationData?.results?.map((plan) => (
                  <TableRow key={plan.unicef_id}>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedAuthorized.includes(plan.unicef_id)}
                        onChange={() =>
                          handleSelect(
                            selectedAuthorized,
                            setSelectedAuthorized,
                            plan.unicef_id,
                          )
                        }
                      />
                    </TableCell>
                    <TableCell>{plan.unicef_id}</TableCell>
                    <TableCell>{plan.status}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </BaseSection>
        </Box>
      )}
      {canReview && (
        <Box mb={6}>
          <BaseSection
            title={t('Payment Plans pending for Release')}
            buttons={
              <ReleasePaymentPlansModal
                selectedPlans={selectedInReview}
                onRelease={() =>
                  bulkAction.mutateAsync({
                    ids: selectedInReview,
                    action: 'RELEASE',
                    comment: 'Released',
                  })
                }
              />
            }
          >
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox />
                  </TableCell>
                  <TableCell>{t('Payment Plan ID')}</TableCell>
                  <TableCell>{t('Status')}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {inReviewData?.results?.map((plan) => (
                  <TableRow key={plan.unicef_id}>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedInReview.includes(plan.unicef_id)}
                        onChange={() =>
                          handleSelect(
                            selectedInReview,
                            setSelectedInReview,
                            plan.unicef_id,
                          )
                        }
                      />
                    </TableCell>
                    <TableCell>{plan.unicef_id}</TableCell>
                    <TableCell>{plan.status}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </BaseSection>
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
