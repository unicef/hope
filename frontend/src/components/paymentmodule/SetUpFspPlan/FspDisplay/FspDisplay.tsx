import { Box, Grid, Typography } from '@material-ui/core';
import CheckCircleOutlineIcon from '@material-ui/icons/CheckCircleOutline';
import WarningIcon from '@material-ui/icons/Warning';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useParams } from 'react-router-dom';
import { LabelizedField } from '../../../core/LabelizedField';
import { Missing } from '../../../core/Missing';
import { Title } from '../../../core/Title';
import { DividerLine } from '../../../core/DividerLine';

const WarnIcon = styled(WarningIcon)`
  color: ${({ theme }) => theme.hctPalette.oragne};
`;

const CheckIcon = styled(CheckCircleOutlineIcon)`
  color: ${({ theme }) => theme.hctPalette.green};
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
        <Grid key={el.id} container>
          <Grid item xs={3}>
            <LabelizedField label={t('FSP')}>{el.name}</LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={`${t('Maximum Amount')} ${'(PLN)'}`}>
              {el.maxAmount}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            {false ? (
              <CheckIcon />
            ) : (
              <Box display='flex' alignItems='center'>
                <WarnIcon />
                {t('Missing')} 2020202020220020202 PLN
              </Box>
            )}
          </Grid>
        </Grid>
      ))}
      <DividerLine />
    </>
  );
}
