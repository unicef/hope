import { Box, Button } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import { useMutation, useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { SurveyCategoryEnum } from '@utils/enums';
import { RecipientsTable } from '../../../tables/Surveys/RecipientsTable/RecipientsTable';
import { UniversalActivityLogTable } from '../../../tables/UniversalActivityLogTable';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { useProgramContext } from '../../../../programContext';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import SurveyDetails from '@components/accountability/Surveys/SurveyDetails';
import { Survey } from '@restgenerated/models/Survey';
import { useHopeDetailsQuery } from '@hooks/useHopeDetailsQuery';

function SurveyDetailsPage(): ReactElement {
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const { id } = useParams();
  const { baseUrl, programId } = useBaseUrl();
  const { isActiveProgram } = useProgramContext();

  const {
    data,
    isLoading: loading,
    error,
  } = useHopeDetailsQuery<Survey>(
    id,
    RestService.restBusinessAreasProgramsSurveysRetrieve,
    {},
  );

  const { data: choicesData, isLoading: choicesLoading } = useQuery({
    queryKey: ['surveyCategoryChoices', baseUrl, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsSurveysCategoryChoicesList({
        businessAreaSlug: baseUrl,
        programSlug: programId,
      }),
  });

  const exportSurveyMutation = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsSurveysExportSampleRetrieve({
        businessAreaSlug: baseUrl,
        programSlug: programId,
        id: id,
      }),
  });
  const permissions = usePermissions();

  if (loading || choicesLoading) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || !choicesData || permissions === null) return null;

  const survey = data; // REST API returns survey directly, not wrapped in { survey }

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Surveys'),
      to: `/${baseUrl}/accountability/surveys`,
    },
  ];

  const exportSurveySample = async (): Promise<void> => {
    try {
      await exportSurveyMutation.mutateAsync();
      showMessage(t('Survey sample exported.'));
    } catch (e) {
      showMessage(e instanceof Error ? e.message : 'An error occurred');
    }
  };

  const renderActions = (): ReactElement => {
    if (survey.category === SurveyCategoryEnum.RAPID_PRO) {
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
    if (survey.category === SurveyCategoryEnum.MANUAL) {
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
export default withErrorBoundary(SurveyDetailsPage, 'SurveyDetailsPage');
