import { Box, Button, Divider, Grid, Typography } from '@material-ui/core';
import { Link, useParams } from 'react-router-dom';
import EditIcon from '@material-ui/icons/EditRounded';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { PageHeader } from '../../../core/PageHeader';
import { Title } from '../../../core/Title';
import { LabelizedField } from '../../../core/LabelizedField';
import { Missing } from '../../../core/Missing';

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
      <Box mt={2} mb={2}>
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
      <Box mt={8} mb={8}>
        <Divider />
      </Box>
    </>
  );
}
