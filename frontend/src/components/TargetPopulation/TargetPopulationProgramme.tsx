import React from 'react';
import styled from 'styled-components';
import { Box, Paper, Typography } from '@material-ui/core';
import { Field } from 'formik';
import { AllProgramsQuery } from '../../__generated__/graphql';
import { OverviewContainer } from '../OverviewContainer';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../LoadingComponent';

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(3)}px;
`;
const GreyText = styled.p`
  color: #9e9e9e;
  font-size: 16px;
`;
const PaperContainer = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

export function TargetPopulationProgramme({
  allPrograms,
  loading,
}: {
  allPrograms: AllProgramsQuery;
  loading: boolean;
}): React.ReactElement {
  const businessArea = useBusinessArea();
  if (loading) return <LoadingComponent />;

  const mappedPrograms = allPrograms.allPrograms.edges.map((edge) => ({
    name: edge.node.name,
    value: edge.node.id,
  }));

  return (
    <PaperContainer data-cy='target-population-program-container'>
      <Title>
        <Typography variant='h6'>Programme</Typography>
      </Title>
      <OverviewContainer>
        <Box display='flex' flexDirection='column'>
          <GreyText>
            Selected programme that the Target Population is created for
          </GreyText>
          <Field
            name='program'
            label='Programme'
            fullWidth
            variant='outlined'
            required
            choices={mappedPrograms}
            component={FormikSelectField}
          />
        </Box>
      </OverviewContainer>
    </PaperContainer>
  );
}
