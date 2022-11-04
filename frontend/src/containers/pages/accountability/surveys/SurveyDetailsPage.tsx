import { Box, Button } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { SurveyDetails } from '../../../../components/accountability/Surveys/SurveyDetails';
import { BreadCrumbsItem } from '../../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { PageHeader } from '../../../../components/core/PageHeader';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { usePermissions } from '../../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../../utils/utils';
import {
  SurveyCategory,
  useExportSurveySampleMutation,
  useSurveyQuery,
} from '../../../../__generated__/graphql';
import { RecipientsTable } from '../../../tables/Surveys/RecipientsTable/RecipientsTable';
import { UniversalActivityLogTable } from '../../../tables/UniversalActivityLogTable';
import { useSnackbar } from '../../../../hooks/useSnackBar';

export const SurveyDetailsPage = (): React.ReactElement => {
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const { data, loading, error } = useSurveyQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const [mutate] = useExportSurveySampleMutation();
  const permissions = usePermissions();

  if (loading) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || permissions === null) return null;

  const { survey } = data;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Surveys'),
      to: `/${businessArea}/accountability/surveys`,
    },
  ];

  const exportSurveySample = async (): Promise<void> => {
    try {
      await mutate({
        variables: {
          surveyId: id,
        },
      });
      showMessage(t('Survey sample exported.'));
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const renderActions = (): React.ReactElement => {
    if (survey.category === SurveyCategory.RapidPro) {
      return (
        <Button variant='contained' color='primary' component={Link} to='/'>
          {t('Check Answers')}
        </Button>
      );
    }
    if (survey.category === SurveyCategory.Manual) {
      if (survey.hasValidSampleFile) {
        return (
          <Button
            download
            variant='contained'
            color='primary'
            href={survey.sampleFilePath}
          >
            {t('Download Survey Sample')}
          </Button>
        );
      }
      return (
        <Button
          variant='contained'
          color='primary'
          onClick={exportSurveySample}
        >
          {t('Export Survey Sample')}
        </Button>
      );
    }
    return null;
  };

  return (
    <>
      <PageHeader
        title={`${survey.unicefId}`}
        breadCrumbs={
          hasPermissions(
            PERMISSIONS.ACCOUNTABILITY_SURVEY_VIEW_DETAILS,
            permissions,
          )
            ? breadCrumbsItems
            : null
        }
      >
        {renderActions()}
      </PageHeader>
      <Box display='flex' flexDirection='column'>
        <SurveyDetails survey={survey} />
        <RecipientsTable
          canViewDetails={hasPermissions(
            PERMISSIONS.ACCOUNTABILITY_SURVEY_VIEW_DETAILS,
            permissions,
          )}
          id={id}
        />
        {hasPermissions(
          PERMISSIONS.ACCOUNTABILITY_SURVEY_VIEW_DETAILS,
          permissions,
        ) && <UniversalActivityLogTable objectId={id} />}
      </Box>
    </>
  );
};
