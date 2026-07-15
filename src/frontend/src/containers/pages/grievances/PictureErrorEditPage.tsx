import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { LoadingButton } from '@components/core/LoadingButton';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { Title } from '@components/core/Title';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PictureErrorEditField } from '@components/grievances/GrievancesPhotoModals/PictureErrorEditField';
import { getGrievanceDetailsPath } from '@components/grievances/utils/createGrievanceUtils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Button, Typography } from '@mui/material';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError, showApiErrorMessages } from '@utils/utils';
import { Formik } from 'formik';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  hasCreatorOrOwnerPermissions,
  PERMISSIONS,
} from '../../../config/permissions';

const PictureErrorEditPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { baseUrl, businessAreaSlug, programCode } = useBaseUrl();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const { id } = useParams();

  const {
    data: ticket,
    isLoading: ticketLoading,
    error,
  } = useQuery<GrievanceTicketDetail>({
    queryKey: ['businessAreasGrievanceTicketsRetrieve', businessAreaSlug, id],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsRetrieve({
        businessAreaSlug,
        id: id,
      }),
  });

  const { data: currentUserData, isLoading: currentUserDataLoading } = useQuery(
    {
      queryKey: ['profile', businessAreaSlug, programCode],
      queryFn: () =>
        RestService.restBusinessAreasUsersProfileRetrieve({
          businessAreaSlug,
          program: programCode === 'all' ? undefined : programCode,
        }),
      staleTime: 5 * 60 * 1000,
      gcTime: 30 * 60 * 1000,
      refetchOnWindowFocus: false,
    },
  );

  const { mutateAsync: updateGrievanceTicket, isPending: loading } =
    useMutation({
      mutationFn: (data: { id: string; formData: any }) =>
        RestService.restBusinessAreasGrievanceTicketsPartialUpdate({
          businessAreaSlug,
          id: data.id,
          formData: data.formData,
        }),
    });

  if (ticketLoading || currentUserDataLoading) return <LoadingComponent />;
  if (isPermissionDeniedError(error))
    return <PermissionDenied permission={PERMISSIONS.GRIEVANCES_UPDATE} />;
  if (!ticket || !currentUserData) return <LoadingComponent />;

  const currentUserId = currentUserData.id;
  const isCreator = ticket.createdBy?.id === currentUserId;
  const isOwner = ticket.assignedTo?.id === currentUserId;

  if (
    !hasCreatorOrOwnerPermissions(
      PERMISSIONS.GRIEVANCES_UPDATE,
      isCreator,
      PERMISSIONS.GRIEVANCES_UPDATE_AS_CREATOR,
      isOwner,
      PERMISSIONS.GRIEVANCES_UPDATE_AS_OWNER,
      permissions,
    )
  )
    return (
      <PermissionDenied
        permission={[
          PERMISSIONS.GRIEVANCES_UPDATE,
          PERMISSIONS.GRIEVANCES_UPDATE_AS_CREATOR,
          PERMISSIONS.GRIEVANCES_UPDATE_AS_OWNER,
        ]}
      />
    );

  const grievanceDetailsPath = getGrievanceDetailsPath(
    ticket.id,
    ticket.category,
    baseUrl,
  );

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Grievance and Feedback'),
      to: grievanceDetailsPath,
    },
  ];

  const photoDetail = ticket.ticketDetails?.individualData?.photo;
  const currentPictureSrc = photoDetail?.value ?? photoDetail?.previousValue;

  return (
    <Formik
      initialValues={{ photo: null }}
      onSubmit={async (values) => {
        try {
          const formData = {
            priority: ticket.priority ?? 0,
            urgency: ticket.urgency ?? 0,
            assignedTo: ticket.assignedTo?.id ?? null,
            language: ticket.language ?? '',
            program: ticket.programs?.[0]?.id,
            extras: {
              individualDataUpdateIssueTypeExtras: {
                individualData: { photo: values.photo },
              },
            },
          };
          await updateGrievanceTicket({ id: ticket.id, formData });
          showMessage(t('Grievance Ticket edited.'));
          navigate(grievanceDetailsPath);
        } catch (e) {
          showApiErrorMessages(e, showMessage);
        }
      }}
    >
      {({ submitForm, values }) => (
        <>
          <PageHeader
            title={`${t('Edit Ticket')} #${ticket.unicefId}`}
            breadCrumbs={breadCrumbsItems}
          >
            <Box display="flex" alignContent="center">
              <Box mr={3}>
                <Button component={Link} to={grievanceDetailsPath}>
                  {t('Cancel')}
                </Button>
              </Box>
              <LoadingButton
                loading={loading}
                disabled={!values.photo}
                color="primary"
                variant="contained"
                onClick={submitForm}
                data-cy="button-submit"
              >
                {t('Save')}
              </LoadingButton>
            </Box>
          </PageHeader>
          <Box p={5}>
            <ContainerColumnWithBorder>
              <Title>
                <Typography variant="h6">{t('Picture')}</Typography>
              </Title>
              <PictureErrorEditField
                currentPhotoSrc={currentPictureSrc}
                fieldName="photo"
              />
            </ContainerColumnWithBorder>
          </Box>
        </>
      )}
    </Formik>
  );
};

export default withErrorBoundary(PictureErrorEditPage, 'PictureErrorEditPage');
