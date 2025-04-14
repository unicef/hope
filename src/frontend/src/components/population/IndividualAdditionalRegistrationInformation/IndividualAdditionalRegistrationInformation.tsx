import { Typography } from '@mui/material';
import Grid from '@mui/material/Grid2';
import Paper from '@mui/material/Paper';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { AllIndividualsFlexFieldsAttributesQuery } from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { IndividualFlexFieldPhotoModal } from '../IndividualFlexFieldPhotoModal';
import { ReactElement } from 'react';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
  margin-top: ${({ theme }) => theme.spacing(6)};
  margin-bottom: ${({ theme }) => theme.spacing(4)};
`;
interface IndividualAdditionalRegistrationInformationProps {
  individual: IndividualDetail;
  flexFieldsData: AllIndividualsFlexFieldsAttributesQuery;
}

export const IndividualAdditionalRegistrationInformation = ({
  individual,
  flexFieldsData,
}: IndividualAdditionalRegistrationInformationProps): ReactElement => {
  const { t } = useTranslation();
  const flexAttributesDict = useArrayToDict(
    flexFieldsData?.allIndividualsFlexFieldsAttributes,
    'name',
    '*',
  );

  const fields = Object.entries(individual?.flexFields || {})
    .filter(([key]) => {
      return flexAttributesDict[key];
    })
    .map(([key, value]: [string, string | string[]]) => {
      if (flexAttributesDict[key]?.type === 'IMAGE') {
        return (
          <LabelizedField
            key={key}
            label={key.replaceAll('_i_f', '').replace(/_/g, ' ')}
          >
            <IndividualFlexFieldPhotoModal field={flexAttributesDict[key]} />
          </LabelizedField>
        );
      }
      if (
        flexAttributesDict[key]?.type === 'SELECT_MANY' ||
        flexAttributesDict[key]?.type === 'SELECT_ONE'
      ) {
        let newValue =
          flexAttributesDict[key].choices.find((item) => item.value === value)
            ?.labelEn || '-';
        if (value instanceof Array) {
          newValue = value
            .map(
              (choice) =>
                flexAttributesDict[key].choices.find(
                  (item) => item.value === choice,
                )?.labelEn || '-',
            )
            .join(', ');
        }
        return (
          <LabelizedField
            key={key}
            label={key.replaceAll('_i_f', '').replace(/_/g, ' ')}
            value={newValue}
          />
        );
      }
      return (
        <LabelizedField
          key={key}
          label={key.replaceAll('_i_f', '').replace(/_/g, ' ')}
          value={value}
        />
      );
    });
  return (
    <Overview>
      <Title>
        <Typography variant="h6">
          {t('Additional Registration information')}
        </Typography>
      </Title>
      <Grid container spacing={6}>
        {fields.map((field, i) => (
          /* eslint-disable-next-line react/no-array-index-key */
          <Grid key={i} size={{ xs: 4 }}>
            {field}
          </Grid>
        ))}
      </Grid>
    </Overview>
  );
};
