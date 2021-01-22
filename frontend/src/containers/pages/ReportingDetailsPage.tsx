import { Button, Grid, Typography } from '@material-ui/core';
import EmailIcon from '@material-ui/icons/Email';
import CheckIcon from '@material-ui/icons/Check';
import { GetApp } from '@material-ui/icons';
import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import {
  useReportChoiceDataQuery,
  useReportQuery,
} from '../../__generated__/graphql';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { ContainerColumnWithBorder } from '../../components/ContainerColumnWithBorder';
import { LabelizedField } from '../../components/LabelizedField';
import { OverviewContainer } from '../../components/OverviewContainer';
import { PageHeader } from '../../components/PageHeader';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../../components/LoadingComponent';
import { StatusBox } from '../../components/StatusBox';
import { reduceChoices, reportStatusToColor } from '../../utils/utils';
import { UniversalMoment } from '../../components/UniversalMoment';
import { usePermissions } from '../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { PermissionDenied } from '../../components/PermissionDenied';

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
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
export const ReportingDetailsPage = (): React.ReactElement => {
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const { data, loading } = useReportQuery({
    variables: { id },
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useReportChoiceDataQuery();

  if (loading || choicesLoading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.REPORTING_EXPORT, permissions))
    return <PermissionDenied />;

  if (!data || !choicesData) return null;
  const { report } = data;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Reporting',
      to: `/${businessArea}/reporting/`,
    },
  ];

  const statusChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.reportStatusChoices);

  const typeChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.reportTypesChoices);

  const FieldsArray: {
    label: string;
    value: React.ReactElement;
    size: boolean | 3 | 6 | 8 | 11 | 'auto' | 1 | 2 | 4 | 5 | 7 | 9 | 10 | 12;
  }[] = [
    {
      label: 'STATUS',
      value: (
        <StatusContainer>
          <StatusBox
            status={statusChoices[report.status]}
            statusToColor={reportStatusToColor}
          />
        </StatusContainer>
      ),
      size: 3,
    },
    {
      label: 'Report Type',
      value: <span>{typeChoices[report.reportType]}</span>,
      size: 3,
    },
    {
      label: 'Timeframe',
      value: (
        <span>
          <UniversalMoment>{report.dateFrom}</UniversalMoment> -{' '}
          <UniversalMoment>{report.dateTo}</UniversalMoment>
        </span>
      ),
      size: 3,
    },
    {
      label: 'Creation Date',
      value: (
        <span>
          <UniversalMoment>{report.createdAt}</UniversalMoment>
        </span>
      ),
      size: 3,
    },
    {
      label: 'Created By',
      value: (
        <span>
          {report.createdBy.firstName} {report.createdBy.lastName}
        </span>
      ),
      size: 3,
    },
    {
      label: 'Programme',
      value: <span>{report.program?.name || '-'}</span>,
      size: 3,
    },
    {
      label: 'Administrative Level 2',
      value: (
        <span>
          {report.adminArea?.edges.map((edge) => edge.node.title).join(', ') ||
            '-'}
        </span>
      ),
      size: 3,
    },
  ];
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
        {report.fileUrl ? (
          <Button
            color='primary'
            variant='contained'
            startIcon={<GetApp />}
            href={report.fileUrl}
          >
            DOWNLOAD REPORT
          </Button>
        ) : null}
      </PageHeader>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>Details</Typography>
        </Title>
        <OverviewContainer>
          <Grid container spacing={6}>
            {FieldsArray.map((el) => (
              <Grid key={el.label} item xs={el.size}>
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
              <EmailIcon fontSize='inherit' />
            </IconContainer>
            <IconContainer>
              <CheckIcon fontSize='inherit' />
            </IconContainer>
          </IconsContainer>
          <GreyText>
            Report was successfully generated and sent to email address of the
            creator.
          </GreyText>
        </>
      )}
    </>
  );
};
