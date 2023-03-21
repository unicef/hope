import { Typography } from '@material-ui/core';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useArrayToDict } from '../../../../../hooks/useArrayToDict';
import {
  AllIndividualsFlexFieldsAttributesQuery,
  ImportedIndividualDetailedFragment,
} from '../../../../../__generated__/graphql';
import { LabelizedField } from '../../../../core/LabelizedField';
import { Title } from '../../../../core/Title';
import { ImportedIndividualFlexFieldPhotoModal } from '../ImportedIndividualFlexFieldPhotoModal';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-top: ${({ theme }) => theme.spacing(6)}px;
  margin-bottom: ${({ theme }) => theme.spacing(6)}px;
`;

interface RegistrationIndividualVulnerabilitiesProps {
  individual: ImportedIndividualDetailedFragment;
  flexFieldsData: AllIndividualsFlexFieldsAttributesQuery;
}

export function RegistrationIndividualVulnerabilities({
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  individual,
  flexFieldsData,
}: RegistrationIndividualVulnerabilitiesProps): React.ReactElement {
  const { t } = useTranslation();
  const flexAttributesDict = useArrayToDict(
    flexFieldsData?.allIndividualsFlexFieldsAttributes,
    'name',
    '*',
  );

  const getLabelOrDash = (choices, value): string =>
    choices.find((item) => item.value === value)?.labelEn || '-';

  const fields = Object.entries(individual.flexFields || {}).map(
    ([key, value]: [string, string | string[]]) => {
      if(key in flexAttributesDict === false)
        return (
          <Grid item xs={4} key={key}>
            <LabelizedField label={key} value={value}>
              {value}
            </LabelizedField>
          </Grid>
        );
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
