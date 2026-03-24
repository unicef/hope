import { Box, FormControlLabel, Radio, RadioGroup } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { SurveyTabsValues } from '@utils/constants';
import { getFilterFromQueryParams } from '@utils/utils';
import LookUpSelectionTablesSurveys from './LookUpSelectionTablesSurveys';
import LookUpTargetPopulationFiltersSurveys from './LookUpTargetPopulationFiltersSurveys';
import withErrorBoundary from '@components/core/withErrorBoundary';

const surveysTabs = ['Whole Program Population', 'Target Population'];

const BoxWithBorderBottom = styled(Box)`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

export function LookUpSelectionSurveys({
  setValues,
  values,
  selectedTab,
  setSelectedTab,
}: {
  setValues;
  values;
  selectedTab;
  setSelectedTab;
}): ReactElement {
  const location = useLocation();

  const initialFilterTP = {
    name: '',
    status: '',
    totalHouseholdsCountMin: '',
    totalHouseholdsCountMax: '',
    createdAtRangeMin: undefined,
    createdAtRangeMax: undefined,
  };

  const [filterTP, setFilterTP] = useState(
    getFilterFromQueryParams(location, initialFilterTP),
  );
  const [appliedFilterTP, setAppliedFilterTP] = useState(
    getFilterFromQueryParams(location, initialFilterTP),
  );

  const { t } = useTranslation();

  const handleChange = (type: number, value: string): void => {
    setValues({
      ...values,
      targetPopulation:
        type === SurveyTabsValues.TARGET_POPULATION && typeof value === 'string'
          ? value
          : '',
    });
  };

  return (
    <Box>
      <BoxWithBorderBottom
        p={4}
        m={4}
        display="flex"
        alignItems="center"
        bgcolor="#F5F5F5"
      >
        <Box pl={5} pr={5} fontWeight="500" fontSize="medium">
          {t('Look up for')}
        </Box>
        <RadioGroup
          aria-labelledby="selection-radio-buttons-group"
          value={selectedTab ?? 0}
          onChange={(event) => {
            setSelectedTab(Number(event.target.value));
          }}
          row
          name="radio-buttons-group"
        >
          {surveysTabs.map((tab, index) => (
            <FormControlLabel
              value={index}
              control={<Radio color="primary" />}
              label={tab}
              key={tab}
            />
          ))}
        </RadioGroup>
      </BoxWithBorderBottom>
      <Box p={4} mt={4}>
        <Box>
          {selectedTab === SurveyTabsValues.WHOLE_PROGRAM_POPULATION && (
            <Box>
              {t('Using whole program population for survey recipients')}
            </Box>
          )}
          {selectedTab === SurveyTabsValues.TARGET_POPULATION && (
            <LookUpTargetPopulationFiltersSurveys
              filter={filterTP}
              setFilter={setFilterTP}
              initialFilter={initialFilterTP}
              appliedFilter={appliedFilterTP}
              setAppliedFilter={setAppliedFilterTP}
            />
          )}
        </Box>
      </Box>
      <LookUpSelectionTablesSurveys
        selectedTab={selectedTab}
        filtersTargetPopulationApplied={appliedFilterTP}
        values={values}
        handleChange={handleChange}
      />
    </Box>
  );
}

export default withErrorBoundary(
  LookUpSelectionSurveys,
  'LookUpSelectionSurveys',
);
