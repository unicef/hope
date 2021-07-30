import { Paper, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const PaperContainer = styled(Paper)`
  display: flex;
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  flex-direction: column;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
  text-align: center;
`;

export function EmptyTable(): React.ReactElement {
  const { t } = useTranslation();
  return (
    <PaperContainer>
      <Typography variant='h6'>{t('No data')}</Typography>
    </PaperContainer>
  );
}
