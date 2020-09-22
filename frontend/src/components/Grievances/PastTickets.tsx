import { Typography } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';
import { ContainerWithBorder } from '../ContainerWithBorder';
import { LabelizedField } from '../LabelizedField';
import { OverviewContainer } from '../OverviewContainer';

export function PastTickets({ tickets }): React.ReactElement {
  const PastContainer = styled.div`
    padding: 22px 22px 22px 0;
  `;
  const Title = styled.div`
    padding-bottom: ${({ theme }) => theme.spacing(8)}px;
  `;

  const formattedTickets = (strings: string[]) =>
    strings ? strings.join(', ') : 'No past tickets';
  return (
    <PastContainer>
      <ContainerWithBorder>
        <Title>
          <Typography variant='h6'>Past tickets</Typography>
        </Title>
        <OverviewContainer>
          <LabelizedField label='TICKET ID'>
            <p>{formattedTickets(tickets)}</p>
          </LabelizedField>
        </OverviewContainer>
      </ContainerWithBorder>
    </PastContainer>
  );
}
