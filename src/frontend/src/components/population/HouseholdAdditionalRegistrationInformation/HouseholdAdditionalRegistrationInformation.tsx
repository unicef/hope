import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { Grid, Theme, Typography } from '@mui/material';
import Paper from '@mui/material/Paper';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { HouseholdFlexFieldPhotoModal } from '../HouseholdFlexFieldPhotoModal';

const Overview = styled(Paper)<{ theme?: Theme }>`
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
  margin-top: 20px;
  &:first-child {
    margin-top: 0px;
  }
`;

interface HouseholdAdditionalRegistrationInformationProps {
  household: HouseholdDetail;
  flexFieldsData: any;
}

export const HouseholdAdditionalRegistrationInformation = ({
  household,
  flexFieldsData,
}: HouseholdAdditionalRegistrationInformationProps): ReactElement => {
  const { t } = useTranslation();

  const flexAttributesDict = useArrayToDict(
    flexFieldsData?.allHouseholdsFlexFieldsAttributes,
    'name',
    '*',
  );

  const fields = Object.entries(household?.flexFields || {}).map(
    ([key, value]: [string, string | string[]]) => {
      if (flexAttributesDict[key]?.type === 'IMAGE') {
        return (
          <LabelizedField
            key={key}
            label={key.replaceAll('_i_f', '').replace(/_/g, ' ')}
          >
            <HouseholdFlexFieldPhotoModal field={flexAttributesDict[key]} />
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
          label={key.replaceAll('_h_f', '').replace(/_/g, ' ')}
          value={value}
        />
      );
    },
  );

  return (
    <div>
      <Overview>
        <Title>
          <Typography variant="h6">
            {t('Additional Registration information')}
          </Typography>
        </Title>
        <Grid container spacing={6}>
          {fields.map((field, i) => (
            <Grid key={i} size={4}>
              {field}
            </Grid>
          ))}
        </Grid>
      </Overview>
    </div>
  );
};
