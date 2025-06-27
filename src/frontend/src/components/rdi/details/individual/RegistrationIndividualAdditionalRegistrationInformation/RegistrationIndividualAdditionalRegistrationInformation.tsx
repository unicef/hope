import { Typography } from '@mui/material';
import Grid from '@mui/material/Grid2';
import Paper from '@mui/material/Paper';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useArrayToDict } from '@hooks/useArrayToDict';
import {
  AllIndividualsFlexFieldsAttributesQuery,
  IndividualDetailedFragment,
} from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { ImportedIndividualFlexFieldPhotoModal } from '../ImportedIndividualFlexFieldPhotoModal';
import { ReactElement } from 'react';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
  margin-top: ${({ theme }) => theme.spacing(6)};
  margin-bottom: ${({ theme }) => theme.spacing(6)};
`;

interface RegistrationIndividualAdditionalRegistrationInformationProps {
  individual: IndividualDetailedFragment;
  flexFieldsData: AllIndividualsFlexFieldsAttributesQuery;
}

export const RegistrationIndividualAdditionalRegistrationInformation = ({
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  individual,
  flexFieldsData,
}: RegistrationIndividualAdditionalRegistrationInformationProps): ReactElement => {
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
      if (key in flexAttributesDict === false) {
        return (
          <Grid size={{ xs:4 }} key={key}>
            <LabelizedField label={key} value={value}>
              {value}
            </LabelizedField>
          </Grid>
        );
      }
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
        <Grid size={{ xs:4 }} key={key}>
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
        <Typography variant="h6">
          {t('Additional Registration information')}
        </Typography>
      </Title>
      <Grid container spacing={6}>
        {fields}
      </Grid>
    </Overview>
  );
};
