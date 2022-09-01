import { Box, Typography } from '@material-ui/core';
import { Field } from 'formik';
import get from 'lodash/get';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { AllProgramsForChoicesQuery } from '../../__generated__/graphql';
import { LoadingComponent } from '../core/LoadingComponent';
import { OverviewContainer } from '../core/OverviewContainer';
import { FormikSelectFieldConfirm } from './FormikSelectFieldConfirm';
import { PaperContainer } from './PaperContainer';

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(3)}px;
`;
const GreyText = styled.p`
  color: #9e9e9e;
  font-size: 16px;
`;

export function TargetPopulationProgramme({
  allPrograms,
  loading,
  program,
}: {
  allPrograms: AllProgramsForChoicesQuery;
  loading: boolean;
  program: string;
}): React.ReactElement {
  const { t } = useTranslation();
  if (loading) return <LoadingComponent />;

  const allProgramsEdges = get(allPrograms, 'allPrograms.edges', []);
  const mappedPrograms = allProgramsEdges.map((edge) => ({
    name: edge.node.name,
    value: edge.node.id,
  }));

  return (
    <PaperContainer data-cy='target-population-program-container'>
      <Title>
        <Typography variant='h6'>{t('Programme')}</Typography>
      </Title>
      <OverviewContainer>
        <Box display='flex' flexDirection='column'>
          <GreyText>
            {t('Selected programme that the Target Population is created for')}
          </GreyText>
          <Field
            name='program'
            label={t('Programme')}
            fullWidth
            variant='outlined'
            required
            choices={mappedPrograms}
            allProgramsEdges={allProgramsEdges}
            component={program ? FormikSelectFieldConfirm : FormikSelectField}
            data-cy='input-program'
          />
        </Box>
      </OverviewContainer>
    </PaperContainer>
  );
}
