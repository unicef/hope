import { Box, Button } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { SurveyDetails } from '@components/accountability/Surveys/SurveyDetails';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import {
  SurveyCategory,
  useExportSurveySampleMutation,
  useSurveyQuery,
  useSurveysChoiceDataQuery,
} from '@generated/graphql';
import { RecipientsTable } from '../../../tables/Surveys/RecipientsTable/RecipientsTable';
import { UniversalActivityLogTable } from '../../../tables/UniversalActivityLogTable';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { useProgramContext } from '../../../../programContext';
import { AdminButton } from '@core/AdminButton';

export function SurveyDetailsPage(): React.ReactElement {
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const { id } = useParams();
  const { baseUrl } = useBaseUrl();
  const { isActiveProgram } = useProgramContext();
  const { data, loading, error } = useSurveyQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const { data: choicesData, loading: choicesLoading } =
    useSurveysChoiceDataQuery({
      fetchPolicy: 'cache-and-network',
    });

  const [mutate] = useExportSurveySampleMutation();
  const permissions = usePermissions();

  if (loading || choicesLoading) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || !choicesData || permissions === null) return null;

  const { survey } = data;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Surveys'),
      to: `/${baseUrl}/accountability/surveys`,
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
        <ButtonTooltip
          variant="contained"
          color="primary"
          component={Link}
          to={{
            pathname: survey?.rapidProUrl,
          }}
          target="_blank"
          title={t('Programme has to be active to export Survey sample')}
          disabled={!isActiveProgram}
        >
          {t('Check Answers')}
        </ButtonTooltip>
      );
    }
    if (survey.category === SurveyCategory.Manual) {
      if (survey.hasValidSampleFile) {
        return (
          <Button
            download
            variant="contained"
            color="primary"
            href={survey.sampleFilePath}
          >
            {t('Download Survey Sample')}
          </Button>
        );
      }
      return (
        <Button
          variant="contained"
          color="primary"
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
        flags={<AdminButton adminUrl={survey.adminUrl} />}
      >
        {renderActions()}
      </PageHeader>
      <Box display="flex" flexDirection="column">
        <SurveyDetails survey={survey} choicesData={choicesData} />
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
}
