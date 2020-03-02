import React, {useState} from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { Typography, Paper } from '@material-ui/core';
import { TargetPopulationPageHeader } from './headers/TargetPopulationPageHeader';
import { Results } from '../../components/TargetPopulation/Results';
import { TargetingCriteria } from '../../components/TargetPopulation/TargetingCriteria';
import { useTargetPopulationQuery } from '../../__generated__/graphql';

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
  const { id } = useParams();
  const { data, loading } = useTargetPopulationQuery({
    variables: {id}
  });
  const [isEdit, setEditState] = useState(false);

  if(!data) {
    return null;
  }
  return (
    <div>
      <TargetPopulationPageHeader isEditMode={isEdit} setEditState={setEditState}/>
      <TargetingCriteria />
      <Results />
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
