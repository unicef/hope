import { Box, Grid, Typography } from '@material-ui/core';
import styled from 'styled-components';
import { Field } from 'formik';
import get from 'lodash/get';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { AllTargetPopulationsQuery } from '../../../../__generated__/graphql';
import { GreyText } from '../../../core/GreyText';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { OverviewContainer } from '../../../core/OverviewContainer';
import { Title } from '../../../core/Title';
import { PaperContainer } from '../../../targeting/PaperContainer';

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

  const allTargetPopulationsEdges = get(
    allTargetPopulations,
    'allTargetPopulation.edges',
    [],
  );
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
                name='targetingId'
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
