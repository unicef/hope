import { Typography } from '@mui/material';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ContainerColumnWithBorder } from '../core/ContainerColumnWithBorder';
import { LabelizedField } from '../core/LabelizedField';
import { Missing } from '../core/Missing';
import { OverviewContainer } from '../core/OverviewContainer';
import { Title } from '../core/Title';

const PastContainer = styled.div`
  padding: 22px 22px 22px 0;
`;

export function PastTickets({ tickets }): React.ReactElement {
  const { t } = useTranslation();
  const formattedTickets = (strings: string[]) => (strings ? strings.join(', ') : t('No past tickets'));
  return (
    <PastContainer>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">
            {t('Past tickets')}
            {' '}
            <Missing />
          </Typography>
        </Title>
        <OverviewContainer>
          <LabelizedField label={t('TICKET ID')}>
            <p>{formattedTickets(tickets)}</p>
          </LabelizedField>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </PastContainer>
  );
}
