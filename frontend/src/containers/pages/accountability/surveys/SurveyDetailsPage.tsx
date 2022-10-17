import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { Box, Button } from '@material-ui/core';
import { BreadCrumbsItem } from '../../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { PageHeader } from '../../../../components/core/PageHeader';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { usePermissions } from '../../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../../utils/utils';
import { useFeedbackQuery } from '../../../../__generated__/graphql';
import { UniversalActivityLogTable } from '../../../tables/UniversalActivityLogTable';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { RecipientsTable } from '../../../tables/Surveys/RecipientsTable/RecipientsTable';
import { SurveyDetails } from '../../../../components/accountability/Surveys/SurveyDetails';

export const SurveyDetailsPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const { data, loading, error } = useFeedbackQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const permissions = usePermissions();

  if (loading) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || permissions === null) return null;

  const survey = data.feedback;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Surveys'),
      to: `/${businessArea}/accountability/surveys`,
    },
  ];
  //TODO:   ACCOUNTABILITY_SURVEYS_VIEW_DETAILS: 'ACCOUNTABILITY_SURVEYS_VIEW_DETAILS',

  return (
    <>
      <PageHeader
        title={`${survey.unicefId}`}
        breadCrumbs={
          hasPermissions(
            PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
            permissions,
          )
            ? breadCrumbsItems
            : null
        }
      >
        <Button variant='contained' color='primary' component={Link} to='/'>
          {t('Check Answers')}
        </Button>
      </PageHeader>
      <Box display='flex' flexDirection='column'>
        <SurveyDetails message={survey} />
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
};
