import { Box, Button } from '@mui/material';
import OpenInNewRoundedIcon from '@mui/icons-material/OpenInNewRounded';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { PaymentRecordDetails } from '@components/payments/PaymentRecordDetails';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import {
  PaymentRecordNode,
  PaymentRecordStatus,
  useBusinessAreaDataQuery,
  useCashAssistUrlPrefixQuery,
  usePaymentRecordQuery,
} from '@generated/graphql';
import { ForceFailedButton } from '@components/payments/ForceFailedButton';
import { RevertForceFailedButton } from '@components/payments/RevertForceFailedButton';
import { useBaseUrl } from '@hooks/useBaseUrl';

export function PaymentRecordDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const { businessArea } = useBaseUrl();
  const { data: businessAreaData, loading: businessAreaDataLoading } =
    useBusinessAreaDataQuery({
      variables: { businessAreaSlug: businessArea },
    });
  const { data: caData, loading: caLoading } = useCashAssistUrlPrefixQuery({
    fetchPolicy: 'cache-first',
  });

  const { data, loading } = usePaymentRecordQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const permissions = usePermissions();
  const { baseUrl, isAllPrograms } = useBaseUrl();
  if (loading || caLoading || businessAreaDataLoading)
    return <LoadingComponent />;
  if (permissions === null) return null;
  if (
    !hasPermissions(
      PERMISSIONS.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
      permissions,
    )
  )
    return <PermissionDenied />;

  if (!data || !caData || !businessAreaData) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: data.paymentRecord.parent.program.name,
      to: `/${baseUrl}/details/${data.paymentRecord.parent.program.id}/`,
    },
    {
      title: `Payment Plan #${data.paymentRecord.parent.caId}`,
      to: `/${baseUrl}/cashplans/${data.paymentRecord.parent.id}`,
    },
  ];
  if (isAllPrograms) {
    breadCrumbsItems.unshift({
      title: t('Programme Management'),
      to: `/${baseUrl}/list/`,
    });
  }
  const paymentRecord = data.paymentRecord as PaymentRecordNode;

  const renderButtons = (): Array<React.ReactElement> => {
    const buttons: Array<React.ReactElement> = [];

    if (
      hasPermissions(
        PERMISSIONS.PAYMENT_VERIFICATION_MARK_AS_FAILED,
        permissions,
      )
    ) {
      const ButtonComponent =
        paymentRecord.status === PaymentRecordStatus.ForceFailed
          ? RevertForceFailedButton
          : ForceFailedButton;
      buttons.push(
        <ButtonComponent
          key={`${paymentRecord.id}-failed`}
          paymentRecordId={paymentRecord.id}
        />,
      );
    }

    if (!businessAreaData.businessArea.isPaymentPlanApplicable) {
      buttons.push(
        <Button
          key={`${paymentRecord.id}-cashAssist`}
          variant="contained"
          color="primary"
          component="a"
          disabled={!paymentRecord.caHashId || !caData?.cashAssistUrlPrefix}
          target="_blank"
          href={`${caData?.cashAssistUrlPrefix}&pagetype=entityrecord&etn=progres_payment&id=${paymentRecord.caHashId}`}
          startIcon={<OpenInNewRoundedIcon />}
        >
          {t('Open in CashAssist')}
        </Button>,
      );
    }
    return buttons;
  };

  return (
    <>
      <PageHeader
        title={`Payment ID ${paymentRecord.caId}`}
        breadCrumbs={breadCrumbsItems}
      >
        <>{renderButtons()}</>
      </PageHeader>
      <Box display="flex" flexDirection="column">
        <PaymentRecordDetails
          paymentRecord={paymentRecord}
          canViewActivityLog={hasPermissions(
            PERMISSIONS.ACTIVITY_LOG_VIEW,
            permissions,
          )}
        />
      </Box>
    </>
  );
}
