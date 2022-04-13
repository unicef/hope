import { Box, Grid, Typography } from '@material-ui/core';
import { Field } from 'formik';
import get from 'lodash/get';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { AllTargetPopulationsQuery } from '../../../__generated__/graphql';
import { LoadingComponent } from '../../core/LoadingComponent';
import { OverviewContainer } from '../../core/OverviewContainer';
import { PaperContainer } from '../../targeting/PaperContainer';

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(3)}px;
`;
const GreyText = styled.p`
  color: #9e9e9e;
  font-size: 16px;
`;
const StyledBox = styled(Box)`
  width: 100%;
`;

export const PaymentPlanTargeting = ({
  allTargetPopulations,
  loading,
}: {
  allTargetPopulations: AllTargetPopulationsQuery;
  loading: boolean;
}): React.ReactElement => {
  const { t } = useTranslation();
  if (loading) return <LoadingComponent />;

  console.log('allTargetPopulations', allTargetPopulations);

  const allTargetPopulationsEdges = get(
    allTargetPopulations,
    'allTargetPopulation.edges',
    [],
  );
  console.log('allTargetPopulationsEdges', allTargetPopulationsEdges);
  const mappedTargetPopulations = allTargetPopulationsEdges.map((edge) => ({
    name: edge.node.name,
    value: edge.node.id,
  }));

  return (
    <PaperContainer>
      <Title>
        <Typography variant='h6'>{t('Targeting')}</Typography>
      </Title>
      <OverviewContainer>
        <StyledBox display='flex' flexDirection='column'>
          <GreyText>{t('Select Target Population')}</GreyText>
          <Grid container>
            <Grid item xs={6}>
              <Field
                name='targetPopulation'
                label={t('Target Population')}
                fullWidth
                variant='outlined'
                required
                choices={mappedTargetPopulations}
                component={FormikSelectField}
              />
            </Grid>
          </Grid>
        </StyledBox>
      </OverviewContainer>
    </PaperContainer>
  );
};
