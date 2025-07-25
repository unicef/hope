import { Box, Grid2 as Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import Close from '@mui/icons-material/Close';
import Edit from '@mui/icons-material/Edit';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LabelizedField } from '@core/LabelizedField';
import { AgencyField } from '../AgencyField';
import { removeItemById } from '../utils/helpers';
import { IndividualIdentity } from '@restgenerated/models/IndividualIdentity';

interface DisabledDivProps {
  disabled: boolean;
}

const DisabledDiv = styled.div<DisabledDivProps>`
  filter: opacity(${({ disabled }) => (disabled ? 0.5 : 1)});
`;

interface Identity {
  id: string;
  number: string;
  partner: string;
  country: string;
  countryIso3: string;
}

interface AddIndividualFieldsData {
  countriesChoices: Array<{ value: any; labelEn?: string }>;
  identityTypeChoices: Array<{ value: any; labelEn?: string }>;
}

export interface EditIdentityRowProps {
  setFieldValue: (field: string, value: any) => void;
  values: any;
  identity: IndividualIdentity;
  arrayHelpers: any;
  addIndividualFieldsData: AddIndividualFieldsData;
  id: number;
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
  const removed = identitiesToRemove.includes(identity.id);
  return isEdited ? (
    <Grid container alignItems="center" spacing={3}>
      <AgencyField
        id={id.toString()}
        key={`${id}-${identity.number}-${identity.partner}`}
        onDelete={() =>
          removeItemById(
            values.individualDataUpdateDocumentsToEdit,
            identity.id.toString(),
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
              country: identity.country.isoCode3,
              partner: identity.partner,
              number: identity.number,
            });
            setEdit(false);
          }}
        >
          <Close />
        </IconButton>
      </Box>
    </Grid>
  ) : (
    <Grid container alignItems="center" spacing={3} key={identity.id}>
      <Grid size={{ xs: 4 }}>
        <DisabledDiv disabled={removed}>
          <LabelizedField label={t('ID AGENCY1')} value={identity.partner} />
        </DisabledDiv>
      </Grid>
      <Grid size={{ xs: 4 }}>
        <DisabledDiv disabled={removed}>
          <LabelizedField label={t('Country')} value={identity.country.name} />
        </DisabledDiv>
      </Grid>
      <Grid size={{ xs: 3 }}>
        <DisabledDiv disabled={removed}>
          <LabelizedField label={t('ID Number')} value={identity.number} />
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
                    identity.id,
                  );
                }}
              >
                <Delete />
              </IconButton>
              <IconButton
                onClick={() => {
                  arrayHelpers.push({
                    id: identity.id,
                    country: identity.country.isoCode3,
                    partner: identity.partner,
                    number: identity.number,
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
