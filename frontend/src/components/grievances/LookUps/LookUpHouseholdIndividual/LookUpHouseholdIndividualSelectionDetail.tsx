import { Box } from '@mui/material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import styled from 'styled-components';
import get from 'lodash/get';
import {
  useAllProgramsForChoicesQuery,
  useHouseholdChoiceDataQuery,
  useIndividualChoiceDataQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { GRIEVANCE_ISSUE_TYPES } from '@utils/constants';
import { getFilterFromQueryParams } from '@utils/utils';
import { LoadingComponent } from '@core/LoadingComponent';
import { Tab, Tabs } from '@core/Tabs';
import { TabPanel } from '@core/TabPanel';
import { HouseholdFilters } from '../../../population/HouseholdFilter';
import { IndividualsFilter } from '../../../population/IndividualsFilter';
import { LookUpHouseholdTable } from '../LookUpHouseholdTable/LookUpHouseholdTable';
import { LookUpIndividualTable } from '../LookUpIndividualTable/LookUpIndividualTable';

const StyledTabs = styled(Tabs)`
  && {
    max-width: 500px;
  }
`;

export function LookUpHouseholdIndividualSelectionDetail({
  onValueChange,
  initialValues,
  selectedIndividual,
  selectedHousehold,
  setSelectedIndividual,
  setSelectedHousehold,
  redirectedFromRelatedTicket,
  isFeedbackWithHouseholdOnly,
}: {
  onValueChange;
  initialValues;
  selectedIndividual;
  selectedHousehold;
  setSelectedIndividual;
  setSelectedHousehold;
  redirectedFromRelatedTicket?: boolean;
  isFeedbackWithHouseholdOnly?: boolean;
}): React.ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const { businessArea, isAllPrograms, programId } = useBaseUrl();
  const [selectedTab, setSelectedTab] = useState(0);
  const initialFilterHH = {
    search: '',
    program: isAllPrograms ? '' : programId,
    searchType: 'household_id',
    residenceStatus: '',
    admin2: '',
    householdSizeMin: '',
    householdSizeMax: '',
    orderBy: 'unicef_id',
    withdrawn: '',
    programState: 'active',
  };
  const initialFilterIND = {
    search: '',
    program: isAllPrograms ? '' : programId,
    searchType: 'individual_id',
    admin2: '',
    sex: '',
    ageMin: '',
    ageMax: '',
    flags: [],
    orderBy: 'unicef_id',
    status: '',
    programState: 'active',
  };

  const { data: householdChoicesData, loading: householdChoicesLoading } =
    useHouseholdChoiceDataQuery();

  const [filterIND, setFilterIND] = useState(
    getFilterFromQueryParams(location, initialFilterIND),
  );
  const [appliedFilterIND, setAppliedFilterIND] = useState(
    getFilterFromQueryParams(location, initialFilterIND),
  );

  const [filterHH, setFilterHH] = useState(
    getFilterFromQueryParams(location, initialFilterHH),
  );
  const [appliedFilterHH, setAppliedFilterHH] = useState(
    getFilterFromQueryParams(location, initialFilterHH),
  );

  const { data: individualChoicesData, loading: individualChoicesLoading } =
    useIndividualChoiceDataQuery();

  const { data: programsData, loading: programsLoading } =
    useAllProgramsForChoicesQuery({
      variables: { businessArea, first: 100 },
      fetchPolicy: 'cache-first',
    });

  if (householdChoicesLoading || individualChoicesLoading || programsLoading)
    return <LoadingComponent />;

  if (!individualChoicesData || !householdChoicesData || !programsData) {
    return null;
  }

  const onSelect = (key, value): void => {
    onValueChange(key, value);
  };

  const allPrograms = get(programsData, 'allPrograms.edges', []);
  const programs = allPrograms.map((edge) => edge.node);

  return (
    <>
      <Box>
        <Box id="scroll-dialog-title">
          <StyledTabs
            value={selectedTab}
            onChange={(_event: React.ChangeEvent<object>, newValue: number) => {
              setSelectedTab(newValue);
            }}
            indicatorColor="primary"
            textColor="primary"
            variant="fullWidth"
            aria-label="look up tabs"
          >
            <Tab label={t('LOOK UP HOUSEHOLD')} />
            <Tab
              disabled={
                initialValues.issueType ===
                  GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL ||
                initialValues.issueType ===
                  GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD ||
                initialValues.issueType === GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD
              }
              label={t('LOOK UP INDIVIDUAL')}
            />
          </StyledTabs>
        </Box>
      </Box>
      <Box>
        <TabPanel value={selectedTab} index={0}>
          <Box mt={2}>
            <HouseholdFilters
              filter={filterHH}
              choicesData={householdChoicesData}
              setFilter={setFilterHH}
              initialFilter={initialFilterHH}
              appliedFilter={appliedFilterHH}
              setAppliedFilter={setAppliedFilterHH}
              isOnPaper={false}
              programs={programs}
            />
          </Box>
          <LookUpHouseholdTable
            filter={appliedFilterHH}
            businessArea={businessArea}
            choicesData={householdChoicesData}
            setFieldValue={onSelect}
            selectedHousehold={selectedHousehold}
            setSelectedHousehold={setSelectedHousehold}
            setSelectedIndividual={setSelectedIndividual}
            redirectedFromRelatedTicket={redirectedFromRelatedTicket}
            isFeedbackWithHouseholdOnly={isFeedbackWithHouseholdOnly}
            noTableStyling
          />
        </TabPanel>
        <TabPanel value={selectedTab} index={1}>
          <IndividualsFilter
            filter={filterIND}
            choicesData={individualChoicesData}
            setFilter={setFilterIND}
            initialFilter={initialFilterIND}
            appliedFilter={appliedFilterIND}
            setAppliedFilter={setAppliedFilterIND}
            isOnPaper={false}
            programs={programs}
          />
          <LookUpIndividualTable
            filter={appliedFilterIND}
            businessArea={businessArea}
            setFieldValue={onSelect}
            valuesInner={initialValues}
            selectedHousehold={selectedHousehold}
            setSelectedHousehold={setSelectedHousehold}
            selectedIndividual={selectedIndividual}
            setSelectedIndividual={setSelectedIndividual}
            noTableStyling
          />
        </TabPanel>
      </Box>
    </>
  );
}
