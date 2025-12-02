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
import { formatNormalCaseValue, renderNestedObject } from '@utils/utils';

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

  if (Object.entries(household?.flexFields || {}).length === 0) {
    return (
      <Overview>
        <Title>
          <Typography variant="h6">
            {t('No additional registration information available')}
          </Typography>
        </Title>
      </Overview>
    );
  }

  const fields = Object.entries(household?.flexFields || {}).map(
    ([key, value]: [string, any]) => {
      // Generate label: remove _h_f, replace underscores, add spaces before uppercase
      const label = key
        .replaceAll('_h_f', '')
        .replace(/_/g, ' ')
        .replace(/([a-z])([A-Z])/g, '$1 $2');
      if (flexAttributesDict[key]?.type === 'IMAGE') {
        return (
          <LabelizedField key={key} label={label}>
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
        if (Array.isArray(value)) {
          newValue = value
            .map(
              (choice) =>
                flexAttributesDict[key].choices.find(
                  (item) => item.value === choice,
                )?.labelEn || '-',
            )
            .join(', ');
        }
        return <LabelizedField key={key} label={label} value={newValue} />;
      }

      // Handle nested objects generically
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        const formattedValue = renderNestedObject(value);
        return (
          <LabelizedField key={key} label={label}>
            <div
              style={{
                whiteSpace: 'pre-line',
                fontFamily: 'monospace',
                fontSize: '0.9em',
              }}
            >
              {formattedValue}
            </div>
          </LabelizedField>
        );
      }

      // Handle arrays
      if (Array.isArray(value)) {
        const displayValue = value
          .map((v) => formatNormalCaseValue(v))
          .join(', ');
        return <LabelizedField key={key} label={label} value={displayValue} />;
      }

      // Handle simple values
      return (
        <LabelizedField
          key={key}
          label={label}
          value={formatNormalCaseValue(value)}
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
