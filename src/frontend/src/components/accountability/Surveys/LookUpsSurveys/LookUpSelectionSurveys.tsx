import { Box, FormControlLabel, Radio, RadioGroup } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import { SurveyTabsValues } from '@utils/constants';
import { getFilterFromQueryParams } from '@utils/utils';
import LookUpProgrammesFiltersSurveys from './LookUpProgrammesFiltersSurveys';
import LookUpSelectionTablesSurveys from './LookUpSelectionTablesSurveys';
import LookUpTargetPopulationFiltersSurveys from './LookUpTargetPopulationFiltersSurveys';
import withErrorBoundary from '@components/core/withErrorBoundary';

const surveysTabs = ['Programme', 'Target Population'];

const BoxWithBorderBottom = styled(Box)`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

export function LookUpSelectionSurveys({
  businessArea,
  onValueChange,
  setValues,
  values,
  selectedTab,
  setSelectedTab,
}: {
  businessArea: string;
  onValueChange;
  setValues;
  values;
  selectedTab;
  setSelectedTab;
}): ReactElement {
  const location = useLocation();
  const initialFilterP = {
    search: '',
    startDate: undefined,
    endDate: undefined,
    status: '',
    sector: [],
    numberOfHouseholdsMin: '',
    numberOfHouseholdsMax: '',
    budgetMin: '',
    budgetMax: '',
    dataCollectingType: '',
  };

  const [filterP, setFilterP] = useState(
    getFilterFromQueryParams(location, initialFilterP),
  );
  const [appliedFilterP, setAppliedFilterP] = useState(
    getFilterFromQueryParams(location, initialFilterP),
  );

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

  // Replace GraphQL query with REST API call
  const { data: choicesData, isLoading: choicesLoading } =
    useQuery<ProgramChoices>({
      queryKey: ['programChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasProgramsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const handleChange = (type: number, value: string): void => {
    setValues({
      ...values,
      program:
        type === SurveyTabsValues.PROGRAM && typeof value !== 'string'
          ? value
          : '',
      targetPopulation:
        type === SurveyTabsValues.TARGET_POPULATION && typeof value === 'string'
          ? value
          : '',
    });
  };

  if (choicesLoading) return null;

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
          value={selectedTab}
          row
          name="radio-buttons-group"
        >
          {surveysTabs.map((tab, index) => (
            <FormControlLabel
              value={index}
              onChange={() => {
                setSelectedTab(index);
              }}
              control={<Radio color="primary" />}
              label={tab}
              key={tab}
            />
          ))}
        </RadioGroup>
      </BoxWithBorderBottom>
      <Box p={4} mt={4}>
        <Box>
          {selectedTab === SurveyTabsValues.PROGRAM && (
            <LookUpProgrammesFiltersSurveys
              filter={filterP}
              choicesData={choicesData}
              setFilter={setFilterP}
              initialFilter={initialFilterP}
              appliedFilter={appliedFilterP}
              setAppliedFilter={setAppliedFilterP}
            />
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
        choicesData={choicesData}
        filtersProgramApplied={appliedFilterP}
        filtersTargetPopulationApplied={appliedFilterTP}
        businessArea={businessArea}
        onValueChange={onValueChange}
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
