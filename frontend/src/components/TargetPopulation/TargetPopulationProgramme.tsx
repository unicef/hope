import React from 'react';
import styled from 'styled-components';
import { Box, Paper, Typography } from '@material-ui/core';
import { Field } from 'formik';
import { ProgramNode, TargetPopulationNode, useAllProgramsQuery } from '../../__generated__/graphql';
import { OverviewContainer } from '../OverviewContainer';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../LoadingComponent';

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(3)}px;
`;
const GreyText = styled.p`
 color: #9E9E9E;
 font-size: 16px;
`
const PaperContainer = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

interface TargetPopulationProgrammeProps {
  targetPopulation: TargetPopulationNode;
}

export function TargetPopulationProgramme({
  targetPopulation,
}: TargetPopulationProgrammeProps): React.ReactElement {
  const {
    program,
  } = targetPopulation;

  const businessArea = useBusinessArea();

  const { data, loading } = useAllProgramsQuery({
    variables: { businessArea },
  });
  if (loading) return <LoadingComponent />;

  const { allPrograms } = data;
  const programs = allPrograms.edges.map((edge) => edge.node);
  return (
    <PaperContainer data-cy='target-population-program-container'>
      <Title>
        <Typography variant='h6'>Programme</Typography>
      </Title>
      <OverviewContainer>
        <Box display="flex" flexDirection="column">
        <GreyText>Selected programme that the Target Population is created for</GreyText>
        <Field
              name='programmeName'
              label='Programme'
              fullWidth
              variant='outlined'
              required
              choices={programs as ProgramNode[]}
              component={FormikSelectField}
        />
        </Box>
      </OverviewContainer>
    </PaperContainer>
  );
}
