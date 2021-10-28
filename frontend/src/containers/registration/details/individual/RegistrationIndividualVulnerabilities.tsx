import { Typography } from '@material-ui/core';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LabelizedField } from '../../../../components/LabelizedField';
import { LoadingComponent } from '../../../../components/LoadingComponent';
import { useArrayToDict } from '../../../../hooks/useArrayToDict';
import {
  ImportedIndividualDetailedFragment,
  useAllIndividualsFlexFieldsAttributesQuery,
} from '../../../../__generated__/graphql';
import { ImportedIndividualFlexFieldPhotoModal } from './ImportedIndividualFlexFieldPhotoModal';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-top: ${({ theme }) => theme.spacing(6)}px;
  margin-bottom: ${({ theme }) => theme.spacing(6)}px;
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface RegistrationIndividualVulnerabilitiesProps {
  individual: ImportedIndividualDetailedFragment;
}

export function RegistrationIndividualVulnerabilities({
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  individual,
}: RegistrationIndividualVulnerabilitiesProps): React.ReactElement {
  const { t } = useTranslation();
  const { data, loading } = useAllIndividualsFlexFieldsAttributesQuery();
  const flexAttributesDict = useArrayToDict(
    data?.allIndividualsFlexFieldsAttributes,
    'name',
    '*',
  );

  if (loading) {
    return <LoadingComponent />;
  }

  if (!data || !flexAttributesDict) {
    return null;
  }

  const getLabelOrDash = (choices, value): string =>
    choices.find((item) => item.value === value)?.labelEn || '-';

  const fields = Object.entries(individual.flexFields || {}).map(
    ([key, value]: [string, string | string[]]) => {
      const { type, choices } = flexAttributesDict[key];
      const label = key.replaceAll('_i_f', '').replace(/_/g, ' ');
      let newValue;
      let children;

      if (type === 'IMAGE') {
        children = (
          <ImportedIndividualFlexFieldPhotoModal
            field={flexAttributesDict[key]}
          />
        );
      } else if (type === 'SELECT_MANY' || type === 'SELECT_ONE') {
        newValue = getLabelOrDash(choices, value);
        if (value instanceof Array) {
          newValue = value
            .map((choice) => getLabelOrDash(choices, choice))
            .join(', ');
        }
      } else {
        newValue = value;
      }
      return (
        <Grid item xs={4} key={key}>
          <LabelizedField label={label} value={newValue}>
            {children}
          </LabelizedField>
        </Grid>
      );
    },
  );
  return (
    <Overview>
      <Title>
        <Typography variant='h6'>{t('Vulnerabilities')}</Typography>
      </Title>
      <Grid container spacing={6}>
        {fields}
      </Grid>
    </Overview>
  );
}
