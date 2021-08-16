import { Box, Grid, IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { AllIndividualsQuery } from '../../__generated__/graphql';
import { LabelizedField } from '../LabelizedField';

const DisabledDiv = styled.div`
  filter: opacity(${({ disabled }) => (disabled ? 0.5 : 1)});
`;
export interface ExistingIdentityFieldArrayProps {
  setFieldValue;
  values;
  individual: AllIndividualsQuery['allIndividuals']['edges'][number]['node'];
}

export function ExistingIdentityFieldArray({
  setFieldValue,
  values,
  individual,
}: ExistingIdentityFieldArrayProps): React.ReactElement {
  const { t } = useTranslation();
  const identitiesToRemove =
    values?.individualDataUpdateIdentitiesToRemove || [];

  const identitiesLabels = individual?.identities?.map((item) => {
    const removed = identitiesToRemove.includes(item.id);
    return (
      <React.Fragment key={item.id}>
        <Grid item xs={4}>
          <DisabledDiv disabled={removed}>
            <LabelizedField label={t('ID AGENCY1')} value={item.agency.label} />
          </DisabledDiv>
        </Grid>
        <Grid item xs={4}>
          <DisabledDiv disabled={removed}>
            <LabelizedField label={t('Country')} value={item.agency.country} />
          </DisabledDiv>
        </Grid>
        <Grid item xs={3}>
          <DisabledDiv disabled={removed}>
            <LabelizedField label={t('ID Number')} value={item.number} />
          </DisabledDiv>
        </Grid>
        <Grid item xs={1}>
          {!removed ? (
            <IconButton
              onClick={() => {
                setFieldValue(
                  `individualDataUpdateIdentitiesToRemove[${identitiesToRemove.length}]`,
                  item.id,
                );
              }}
            >
              <Delete />
            </IconButton>
          ) : (
            <Box display='flex' alignItems='center' height={48} color='red'>
              {t('REMOVED')}
            </Box>
          )}
        </Grid>
      </React.Fragment>
    );
  });
  return (
    <Grid container spacing={3}>
      {identitiesLabels}
    </Grid>
  );
}
