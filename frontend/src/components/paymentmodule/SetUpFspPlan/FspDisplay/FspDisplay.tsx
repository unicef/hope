import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useParams } from 'react-router-dom';
import { LabelizedField } from '../../../core/LabelizedField';
import { Missing } from '../../../core/Missing';
import { Title } from '../../../core/Title';

const DividerContainer = styled.div`
  height: 50px;
  width: 100%;
  display: flex;
  align-items: center;
`;
const Divider = styled.div`
  border-top: 1px solid #b1b1b5;
  height: 1px;
  width: 100%;
`;

interface FspDisplayProps {
  fsp;
}

export function FspDisplay({ fsp }: FspDisplayProps): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();

  return (
    <>
      <Box mt={4}>
        <Title>
          <Typography variant='h6'>{fsp.name}</Typography>
        </Title>
      </Box>
      <Grid container>
        <Grid item xs={3}>
          <LabelizedField label={`${t('To be delivered')} ${'PLN'}`}>
            <Missing />
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={`${t('Total Maximum Amount')} ${'PLN'}`}>
            <Missing />
          </LabelizedField>
        </Grid>
      </Grid>
      <Box mt={4} mb={4}>
        <Typography>Order</Typography>
      </Box>
      {fsp.fsps?.map((el) => (
        <Grid container>
          <Grid key={el.id} item xs={3}>
            <LabelizedField label={t('FSP')}>{el.name}</LabelizedField>
          </Grid>
          <Grid key={el.id} item xs={3}>
            <LabelizedField label={`${t('Maximum Amount')} ${'(PLN)'}`}>
              {el.maxAmount}
            </LabelizedField>
          </Grid>
        </Grid>
      ))}
      <DividerContainer>
        <Divider />
      </DividerContainer>
    </>
  );
}
