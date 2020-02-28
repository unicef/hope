import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Button, Typography, Paper } from '@material-ui/core';
import { EditRounded } from '@material-ui/icons';
import { PageHeader } from '../../components/PageHeader';
import { TargetingCriteria } from '../../components/TargetPopulation/TargetingCriteria';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';

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

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export function TargetPopulationDetailsPage() {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Target Population',
      to: `/${businessArea}/target-population/`,
    },
  ];
  return (
    <div>
      <PageHeader title={t('Population')} breadCrumbs={breadCrumbsItems}>
        <>
          <ButtonContainer>
            <Button variant='outlined' color='primary' startIcon={<EditRounded />}>
              Edit
            </Button>
          </ButtonContainer>
          <ButtonContainer>
            <Button variant='contained' color='primary'>
              Finalize
            </Button>
          </ButtonContainer>
        </>
      </PageHeader>
      <TargetingCriteria />
      <PaperContainer>
        <Title>
          <Typography variant='h6'>Results</Typography>
        </Title>
      </PaperContainer>
      <PaperContainer>
        <Title>
          <Typography variant='h6'>
            Target Population Entries (Households)
          </Typography>
        </Title>
      </PaperContainer>
    </div>
  );
}
