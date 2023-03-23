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
import { removeItemById } from '../utils/helpers';

const DisabledDiv = styled.div`
  filter: opacity(${({ disabled }) => (disabled ? 0.5 : 1)});
`;

export interface EditIdentityRowProps {
  setFieldValue;
  values;
  identity: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['identities']['edges'][number];
  arrayHelpers;
  addIndividualFieldsData: AllAddIndividualFieldsQuery;
  id: string;
}

export function EditIdentityRow({
  setFieldValue,
  values,
  identity,
  arrayHelpers,
  addIndividualFieldsData,
  id,
}: EditIdentityRowProps): React.ReactElement {
  const { t } = useTranslation();
  const [isEdited, setEdit] = useState(false);
  const identitiesToRemove =
    values?.individualDataUpdateIdentitiesToRemove || [];
  const removed = identitiesToRemove.includes(identity.node.id);
  return isEdited ? (
    <>
      <AgencyField
        id={id}
        key={`${id}-${identity?.node?.number}-${identity?.node?.partner}`}
        onDelete={() =>
          removeItemById(
            values.individualDataUpdateDocumentsToEdit,
            identity.node.id,
            arrayHelpers,
          )
        }
        countryChoices={addIndividualFieldsData.countriesChoices}
        identityTypeChoices={addIndividualFieldsData.identityTypeChoices}
        baseName='individualDataUpdateIdentitiesToEdit'
        isEdited={isEdited}
        values={values}
      />
      <Box display='flex' alignItems='center'>
        <IconButton
          onClick={() => {
            arrayHelpers.remove({
              country: identity.node.countryIso3,
              partner: identity.node.partner,
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
            value={identity.node.partner}
          />
        </DisabledDiv>
      </Grid>
      <Grid item xs={4}>
        <DisabledDiv disabled={removed}>
          <LabelizedField label={t('Country')} value={identity.node.country} />
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
                arrayHelpers.push({
                  id: identity.node.id,
                  country: identity.node.countryIso3,
                  partner: identity.node.partner,
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
