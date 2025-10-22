import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { Box } from '@mui/material';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { MessageDetail } from '@restgenerated/models/MessageDetail';
import { UniversalActivityLogTable } from '../../../tables/UniversalActivityLogTable';
import RecipientsTable from '../../../tables/Communication/RecipientsTable/RecipientsTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { AdminButton } from '@core/AdminButton';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import CommunicationMessageDetails from '@components/accountability/Communication/CommunicationMessageDetails';
import CommunicationDetails from '@components/accountability/Communication/CommunicationDetails';

function CommunicationDetailsPage(): ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const { businessArea, baseUrl, programSlug } = useBaseUrl();

  const {
    data: message,
    isLoading,
    error,
  } = useQuery<MessageDetail>({
    queryKey: [
      'accountabilityCommunicationMessage',
      businessArea,
      id,
      programSlug,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsMessagesRetrieve({
        businessAreaSlug: businessArea,
        id: id,
        programSlug,
      }),
    enabled: !!id && !!businessArea,
  });

  const permissions = usePermissions();

  if (isLoading) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!message || permissions === null) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Communication'),
      to: `/${baseUrl}/accountability/communication`,
    },
  ];
  return (
    <>
      <PageHeader
        title={`${message.unicefId}`}
        breadCrumbs={
          hasPermissions(
            PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
            permissions,
          )
            ? breadCrumbsItems
            : null
        }
        flags={<AdminButton adminUrl={message.adminUrl} />}
      />
      <Box display="flex" flexDirection="column">
        <CommunicationDetails message={message} />
        <CommunicationMessageDetails message={message} />
        <RecipientsTable
          canViewDetails={hasPermissions(
            PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
            permissions,
          )}
          id={id}
        />
        {hasPermissions(
          PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
          permissions,
        ) && <UniversalActivityLogTable objectId={id} />}
      </Box>
    </>
  );
}

export default withErrorBoundary(
  CommunicationDetailsPage,
  'CommunicationDetailsPage',
);
