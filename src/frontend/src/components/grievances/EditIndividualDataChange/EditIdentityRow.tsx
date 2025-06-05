import { Box, Grid2 as Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import Close from '@mui/icons-material/Close';
import Edit from '@mui/icons-material/Edit';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllAddIndividualFieldsQuery,
  AllIndividualsQuery,
} from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { AgencyField } from '../AgencyField';
import { removeItemById } from '../utils/helpers';

interface DisabledDivProps {
  disabled: boolean;
}

const DisabledDiv = styled.div<DisabledDivProps>`
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
}: EditIdentityRowProps): ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.includes('edit-ticket');
  const { t } = useTranslation();
  const [isEdited, setEdit] = useState(false);
  const identitiesToRemove =
    values?.individualDataUpdateIdentitiesToRemove || [];
  const removed = identitiesToRemove.includes(identity.node.id);
  return isEdited ? (
    <Grid container alignItems="center" spacing={3}>
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
        baseName="individualDataUpdateIdentitiesToEdit"
        isEdited={isEdited}
        values={values}
      />
      <Box display="flex" alignItems="center">
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
    </Grid>
  ) : (
    <Grid container alignItems="center" spacing={3} key={identity.node.id}>
      <Grid size={{ xs: 4 }}>
        <DisabledDiv disabled={removed}>
          <LabelizedField
            label={t('ID AGENCY1')}
            value={identity.node.partner}
          />
        </DisabledDiv>
      </Grid>
      <Grid size={{ xs: 4 }}>
        <DisabledDiv disabled={removed}>
          <LabelizedField label={t('Country')} value={identity.node.country} />
        </DisabledDiv>
      </Grid>
      <Grid size={{ xs: 3 }}>
        <DisabledDiv disabled={removed}>
          <LabelizedField label={t('ID Number')} value={identity.node.number} />
        </DisabledDiv>
      </Grid>
      <Grid size={{ xs: 1 }}>
        {!removed ? (
          !isEditTicket && (
            <Box display="flex" alignItems="center">
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
          )
        ) : (
          <Box display="flex" alignItems="center" height={48} color="red">
            {t('REMOVED')}
          </Box>
        )}
      </Grid>
    </Grid>
  );
}
