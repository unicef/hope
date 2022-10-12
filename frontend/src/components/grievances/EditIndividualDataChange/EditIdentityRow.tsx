import { Box, Grid, IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import Close from '@material-ui/icons/Close';
import Edit from '@material-ui/icons/Edit';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllAddIndividualFieldsQuery,
  AllIndividualsQuery,
} from '../../../__generated__/graphql';
import { LabelizedField } from '../../core/LabelizedField';
import { AgencyField } from '../AgencyField';

const DisabledDiv = styled.div`
  filter: opacity(${({ disabled }) => (disabled ? 0.5 : 1)});
`;

export interface EditIdentityRowProps {
  setFieldValue;
  values;
  identity: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['identities']['edges'][number];
  arrayHelpers;
  addIndividualFieldsData: AllAddIndividualFieldsQuery;
  index;
}

export function EditIdentityRow({
  setFieldValue,
  values,
  identity,
  arrayHelpers,
  addIndividualFieldsData,
  index,
}: EditIdentityRowProps): React.ReactElement {
  const { t } = useTranslation();
  const [isEdited, setEdit] = useState(false);
  const identitiesToRemove =
    values?.individualDataUpdateIdentitiesToRemove || [];
  const removed = identitiesToRemove.includes(identity.node.id);
  return isEdited ? (
    <>
      <AgencyField
        index={index}
        key={`${index}-${identity?.node?.number}-${identity?.node?.agency}`}
        onDelete={() => arrayHelpers.remove(index)}
        countryChoices={addIndividualFieldsData.countriesChoices}
        identityTypeChoices={addIndividualFieldsData.identityTypeChoices}
        baseName='individualDataUpdateIdentitiesToEdit'
        isEdited={isEdited}
      />
      <Box display='flex' alignItems='center'>
        <IconButton
          onClick={() => {
            arrayHelpers.remove({
              country: identity.node.agency.countryIso3,
              agency: identity.node.agency.label,
              number: identity.node.number,
            });
            setEdit(false);
          }}
        >
          <Close />
        </IconButton>
      </Box>
    </>
  ) : (
    <React.Fragment key={identity.node.id}>
      <Grid item xs={4}>
        <DisabledDiv disabled={removed}>
          <LabelizedField
            label={t('ID AGENCY1')}
            value={identity.node.agency.label}
          />
        </DisabledDiv>
      </Grid>
      <Grid item xs={4}>
        <DisabledDiv disabled={removed}>
          <LabelizedField
            label={t('Country')}
            value={identity.node.agency.country}
          />
        </DisabledDiv>
      </Grid>
      <Grid item xs={3}>
        <DisabledDiv disabled={removed}>
          <LabelizedField label={t('ID Number')} value={identity.node.number} />
        </DisabledDiv>
      </Grid>
      <Grid item xs={1}>
        {!removed ? (
          <Box display='flex' align-items='center'>
            <IconButton
              onClick={() => {
                setFieldValue(
                  `individualDataUpdateIdentitiesToRemove[${identitiesToRemove.length}]`,
                  identity.node.id,
                );
              }}
            >
              <Delete />
            </IconButton>
            <IconButton
              onClick={() => {
                arrayHelpers.replace(index, {
                  id: identity.node.id,
                  country: identity.node.agency.countryIso3,
                  agency: identity.node.agency.label,
                  number: identity.node.number,
                });
                setEdit(true);
              }}
            >
              <Edit />
            </IconButton>
          </Box>
        ) : (
          <Box display='flex' alignItems='center' height={48} color='red'>
            {t('REMOVED')}
          </Box>
        )}
      </Grid>
    </React.Fragment>
  );
}
