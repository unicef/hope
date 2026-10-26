import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { useArrayToDict } from '@hooks/useArrayToDict';
import type { Theme } from '@mui/material';
import { Typography } from '@mui/material';
import Paper from '@mui/material/Paper';
import type { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ResponsiveGrid,
  ResponsiveGridContainer,
  SECTION_PADDING,
} from 'src/responsive';
import styled from 'styled-components';
import { ImportedIndividualFlexFieldPhotoModal } from '../ImportedIndividualFlexFieldPhotoModal';

const Overview = styled(Paper)<{ theme?: Theme }>`
  margin-top: ${({ theme }) => theme.spacing(6)};
  margin-bottom: ${({ theme }) => theme.spacing(6)};
`;

interface RegistrationIndividualAdditionalRegistrationInformationProps {
  individual: IndividualDetail;
  flexFieldsData: any;
}

export const RegistrationIndividualAdditionalRegistrationInformation = ({
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
          <ResponsiveGrid size="third" key={key}>
            <LabelizedField label={key} value={value}>
              {value}
            </LabelizedField>
          </ResponsiveGrid>
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
        <ResponsiveGrid size="third" key={key}>
          <LabelizedField label={label} value={newValue}>
            {children}
          </LabelizedField>
        </ResponsiveGrid>
      );
    },
  );
  return (
    <Overview sx={{ padding: SECTION_PADDING }}>
      <Title>
        <Typography variant="h6">
          {t('Additional Registration information')}
        </Typography>
      </Title>
      <ResponsiveGridContainer spacing={6}>{fields}</ResponsiveGridContainer>
    </Overview>
  );
};
