import { Button, Grid2 as Grid, Typography } from '@mui/material';
import { GetApp } from '@mui/icons-material';
import CheckIcon from '@mui/icons-material/Check';
import EmailIcon from '@mui/icons-material/Email';
import { ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { ALL_REPORTS_QUERY } from '../../../apollo/queries/reporting/AllReports';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { LabelizedField } from '@components/core/LabelizedField';
import { LoadingButton } from '@components/core/LoadingButton';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { OverviewContainer } from '@components/core/OverviewContainer';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { StatusBox } from '@components/core/StatusBox';
import { Title } from '@components/core/Title';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { REPORTING_STATES } from '@utils/constants';
import { choicesToDict, reportStatusToColor } from '@utils/utils';
import {
  useReportChoiceDataQuery,
  useReportQuery,
  useRestartCreateReportMutation,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import withErrorBoundary from '@components/core/withErrorBoundary';

const IconContainer = styled.div`
  color: #d1d1d1;
  font-size: 90px;
`;
const GreyText = styled.div`
  color: #abacae;
  font-size: 24px;
  text-align: center;
`;

const IconsContainer = styled.div`
  margin-top: 120px;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 50px;
`;

function ReportingDetailsPage(): ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const { baseUrl, businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();

  const [mutate, { loading: restartReportLoading }] =
    useRestartCreateReportMutation();

  const { data, loading, startPolling, stopPolling } = useReportQuery({
    variables: { id },
  });
  const { data: choicesData, loading: choicesLoading } =
    useReportChoiceDataQuery();

  useEffect(() => {
    if (data?.report?.status === REPORTING_STATES.PROCESSING) {
      startPolling(30000);
    } else {
      stopPolling();
    }
    return stopPolling;
  }, [data, startPolling, stopPolling]);

  if (loading || choicesLoading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.REPORTING_EXPORT, permissions))
    return <PermissionDenied />;

  if (!data || !choicesData) return null;
  const { report } = data;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Reporting'),
      to: `/${baseUrl}/reporting/`,
    },
  ];

  const statusChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.reportStatusChoices);

  const typeChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.reportTypesChoices);

  const FieldsArray: {
    label: string;
    value: ReactElement | string;
    size: number
  }[] = [
    {
      label: t('STATUS'),
      value: (
        <StatusBox
          status={statusChoices[report.status]}
          statusToColor={reportStatusToColor}
        />
      ),
      size: 3,
    },
    {
      label: t('Report Type'),
      value: typeChoices[report.reportType],
      size: 3,
    },
    {
      label: t('Timeframe'),
      value: (
        <span>
          <UniversalMoment>{report.dateFrom}</UniversalMoment> -{' '}
          <UniversalMoment>{report.dateTo}</UniversalMoment>
        </span>
      ),
      size: 3,
    },
    {
      label: t('Creation Date'),
      value: <UniversalMoment>{report.createdAt}</UniversalMoment>,
      size: 3,
    },
    {
      label: t('Created By'),
      value: (
        <span>
          {report.createdBy.firstName} {report.createdBy.lastName}
        </span>
      ),
      size: 3,
    },
    {
      label: t('Programme'),
      value: report.program?.name,
      size: 3,
    },
    {
      label: t('Administrative Level 1'),
      value: (
        <span>
          {report.adminArea1?.edges.map((edge) => edge.node.name).join(', ') ||
            '-'}
        </span>
      ),
      size: 3,
    },
    {
      label: t('Administrative Level 2'),
      value: (
        <span>
          {report.adminArea2?.edges.map((edge) => edge.node.name).join(', ') ||
            '-'}
        </span>
      ),
      size: 3,
    },
  ];

  const currentDate: Date = new Date();
  const lastUpdatedDate: Date = new Date(report.updatedAt);
  const minutes: number = Math.floor(
    (currentDate.getTime() - lastUpdatedDate.getTime()) / 60000,
  );

  const reGenerateReport = async (): Promise<void> => {
    try {
      const response = await mutate({
        variables: {
          reportData: { reportId: report.id, businessAreaSlug: businessArea },
        },
        refetchQueries: () => [
          { query: ALL_REPORTS_QUERY, variables: { businessArea } },
        ],
      });
      if (!response.errors && response.data.restartCreateReport) {
        showMessage(t('Re-Generating Report'));
      } else {
        showMessage(t('Re-Generating Report action failed.'));
      }
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  return (
    <>
      <PageHeader
        title={
          <span>
            {typeChoices[report.reportType]}{' '}
            <UniversalMoment>{report.createdAt}</UniversalMoment>
          </span>
        }
        breadCrumbs={breadCrumbsItems}
      >
        <>
          {report.fileUrl && (
            <Button
              color="primary"
              variant="contained"
              startIcon={<GetApp />}
              href={report.fileUrl}
            >
              {t('DOWNLOAD REPORT')}
            </Button>
          )}
          {report.status === REPORTING_STATES.PROCESSING && minutes > 30 && (
            <>
              <span>
                {t('Report is in processing status for over 30 min.')}
                <br />
                {t('Please wait or re-generate report.')}
              </span>
              &emsp;
              <LoadingButton
                color="primary"
                variant="contained"
                loading={restartReportLoading}
                onClick={() => {
                  reGenerateReport();
                }}
              >
                {t('Re-Generate Report')}
              </LoadingButton>
            </>
          )}
        </>
      </PageHeader>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">{t('Details')}</Typography>
        </Title>
        <OverviewContainer>
          <Grid container spacing={6}>
            {FieldsArray.map((el) => (
              <Grid key={el.label} size={{ xs: el.size }}>
                <LabelizedField label={el.label}>{el.value}</LabelizedField>
              </Grid>
            ))}
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
      {report.status === 2 && (
        <>
          <IconsContainer>
            <IconContainer>
              <EmailIcon fontSize="inherit" />
            </IconContainer>
            <IconContainer>
              <CheckIcon fontSize="inherit" />
            </IconContainer>
          </IconsContainer>
          <GreyText>
            {t(
              'Report was successfully generated and sent to email address of the creator.',
            )}
          </GreyText>
        </>
      )}
    </>
  );
}

export default withErrorBoundary(ReportingDetailsPage, 'ReportingDetailsPage');
