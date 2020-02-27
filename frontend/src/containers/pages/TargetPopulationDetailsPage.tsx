import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Button, Typography, Paper } from '@material-ui/core';
import { PageHeader } from '../../components/PageHeader';
import { TargetingCriteria } from '../../components/targetPopulation/TargetingCriteria';

const PaperContainer = styled(Paper)`
  display: flex;
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  flex-direction: column;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;


export function TargetPopulationDetailsPage() {
  const { t } = useTranslation();

  return (
    <div>
      <PageHeader title={t('Population')}>
        <Button variant='contained' color='primary' disabled>
          Save
        </Button>
      </PageHeader>
      <TargetingCriteria />
      <PaperContainer>
        <Title>
          <Typography variant='h6'>Results</Typography>
        </Title>
      </PaperContainer>
      <PaperContainer>
        <Title>
          <Typography variant='h6'>Target Population Entries (Households)</Typography>
        </Title>
      </PaperContainer>
    </div>
  );
}
