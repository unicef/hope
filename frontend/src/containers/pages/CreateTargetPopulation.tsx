import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Button } from '@material-ui/core';
import { PageHeader } from '../../components/PageHeader';

const Container = styled.div`
  && {
    display: flex;
    flex-direction: column;
    min-width: 100%;
  }
`;

export function CreateTargetPopulation() {
  const { t } = useTranslation();

  return (
    <div>
      <PageHeader title={t('Population')}>
        <Button variant='contained' color='primary'>
          Create new
        </Button>
      </PageHeader>
      <Container>
        dupa
      </Container>
    </div>
  );
}
