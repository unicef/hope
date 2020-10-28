import { Typography } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { LabelizedField } from '../LabelizedField';
import { OverviewContainer } from '../OverviewContainer';

const PastContainer = styled.div`
  padding: 22px 22px 22px 0;
`;
const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function PastTickets({ tickets }): React.ReactElement {
  const formattedTickets = (strings: string[]) =>
    strings ? strings.join(', ') : 'No past tickets';
  return (
    <PastContainer>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>Past tickets</Typography>
        </Title>
        <OverviewContainer>
          <LabelizedField label='TICKET ID'>
            <p>{formattedTickets(tickets)}</p>
          </LabelizedField>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </PastContainer>
  );
}
