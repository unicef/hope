import { Grid, Paper, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LabelizedField } from '../LabelizedField';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-bottom: ${({ theme }) => theme.spacing(6)}px;
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function CashPlus({ individual }): React.ReactElement {
  const { t } = useTranslation();
  const { enrolledInNutritionProgramme, administrationOfRutf } = individual;
  return (
    <Overview>
      <Title>
        <Typography variant='h6'>{t('Cash+')}</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid item xs={4}>
          <LabelizedField
            label={t('Enrolled in nutrition programme')}
            value={enrolledInNutritionProgramme ? t('YES') : t('NO')}
          />
        </Grid>
        <Grid item xs={4}>
          <LabelizedField
            label={t('Administratiion of rutf')}
            value={administrationOfRutf ? t('YES') : t('NO')}
          />
        </Grid>
      </Grid>
    </Overview>
  );
}
