import { Button, Grid, Typography } from '@material-ui/core';
import EmailIcon from '@material-ui/icons/Email';
import CheckIcon from '@material-ui/icons/Check';
import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { ContainerColumnWithBorder } from '../../components/ContainerColumnWithBorder';
import { LabelizedField } from '../../components/LabelizedField';
import { Missing } from '../../components/Missing';
import { OverviewContainer } from '../../components/OverviewContainer';
import { PageHeader } from '../../components/PageHeader';
import { StatusBox } from '../../components/StatusBox';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { decodeIdString } from '../../utils/utils';
import { GetApp } from '@material-ui/icons';

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
export const ReportingDetailsPage = () => {
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Reporting',
      to: `/${businessArea}/reporting/`,
    },
  ];

  const FieldsArray: {
    label: string;
    value: React.ReactElement;
    size: boolean | 3 | 6 | 8 | 11 | 'auto' | 1 | 2 | 4 | 5 | 7 | 9 | 10 | 12;
  }[] = [
    {
      label: 'STATUS',
      value: (
        <StatusContainer>
          {/* <StatusBox
            status={''}
            statusToColor={}
          /> */}
          <Missing />
        </StatusContainer>
      ),
      size: 3,
    },
    {
      label: 'Report Type',
      value: (
        <span>
          <Missing />
        </span>
      ),
      size: 3,
    },
    {
      label: 'Timeframe',
      value: (
        <span>
          <Missing />
        </span>
      ),
      size: 3,
    },
    {
      label: 'Administrative Level 2',
      value: (
        <span>
          <Missing />
        </span>
      ),
      size: 3,
    },
    {
      label: 'Programme',
      value: (
        <span>
          <Missing />
        </span>
      ),
      size: 3,
    },
    {
      label: 'Created By',
      value: (
        <span>
          <Missing />
        </span>
      ),
      size: 3,
    },
    {
      label: 'Creation Date',
      value: (
        <span>
          <Missing />
        </span>
      ),
      size: 3,
    },
  ];
  return (
    <>
      <PageHeader
        title={`Report title and date ${id}`}
        breadCrumbs={breadCrumbsItems}
      >
        <>
          <Button
            color='primary'
            variant='contained'
            startIcon={<GetApp />}
            onClick={() => console.log('REPORT DOWNLOADED')}
          >
            DOWNLOAD
          </Button>
        </>
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
  );
};
