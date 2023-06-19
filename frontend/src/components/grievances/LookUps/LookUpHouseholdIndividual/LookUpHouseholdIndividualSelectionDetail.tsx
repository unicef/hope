import { Box, Tab, Tabs } from '@material-ui/core';
import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  ProgramNode,
  useAllProgramsForChoicesQuery,
  useHouseholdChoiceDataQuery,
  useIndividualChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { GRIEVANCE_ISSUE_TYPES } from '../../../../utils/constants';
import { getFilterFromQueryParams } from '../../../../utils/utils';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { TabPanel } from '../../../core/TabPanel';
import { HouseholdFilters } from '../../../population/HouseholdFilter';
import { IndividualsFilter } from '../../../population/IndividualsFilter';
import { LookUpHouseholdTable } from '../LookUpHouseholdTable/LookUpHouseholdTable';
import { LookUpIndividualTable } from '../LookUpIndividualTable/LookUpIndividualTable';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';

const StyledTabs = styled(Tabs)`
  && {
    max-width: 500px;
  }
`;

export const LookUpHouseholdIndividualSelectionDetail = ({
  onValueChange,
  initialValues,
  selectedIndividual,
  selectedHousehold,
  setSelectedIndividual,
  setSelectedHousehold,
  redirectedFromRelatedTicket,
}: {
  onValueChange;
  initialValues;
  selectedIndividual;
  selectedHousehold;
  setSelectedIndividual;
  setSelectedHousehold;
  redirectedFromRelatedTicket?: boolean;
}): React.ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const [selectedTab, setSelectedTab] = useState(0);
  const initialFilterHH = {
    search: '',
    program: '',
    residenceStatus: '',
    admin2: '',
    householdSizeMin: '',
    householdSizeMax: '',
    orderBy: 'unicef_id',
    withdrawn: null,
  };
  const initialFilterIND = {
    search: '',
    admin2: '',
    sex: '',
    ageMin: '',
    ageMax: '',
    flags: [],
    orderBy: 'unicef_id',
    status: '',
  };

  const { businessArea } = useBaseUrl();
  const {
    data: programsData,
    loading: programsLoading,
  } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: householdChoicesData,
    loading: householdChoicesLoading,
  } = useHouseholdChoiceDataQuery();

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

  const {
    data: individualChoicesData,
    loading: individualChoicesLoading,
  } = useIndividualChoiceDataQuery();

  if (householdChoicesLoading || individualChoicesLoading || programsLoading)
    return <LoadingComponent />;

  if (!individualChoicesData || !householdChoicesData || !programsData) {
    return null;
  }

  const { allPrograms } = programsData;
  const programs = allPrograms.edges.map((edge) => edge.node);

  const onSelect = (key, value): void => {
    onValueChange(key, value);
  };

  return (
    <>
      <Box>
        <Box id='scroll-dialog-title'>
          <StyledTabs
            value={selectedTab}
            onChange={(_event: React.ChangeEvent<{}>, newValue: number) => {
              setSelectedTab(newValue);
            }}
            indicatorColor='primary'
            textColor='primary'
            variant='fullWidth'
            aria-label='look up tabs'
          >
            <Tab label={t('LOOK UP HOUSEHOLD')} />
            <Tab
              disabled={
                initialValues.issueType ===
                  GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL ||
                initialValues.issueType ===
                  GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD
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
              programs={programs as ProgramNode[]}
              filter={filterHH}
              choicesData={householdChoicesData}
              setFilter={setFilterHH}
              initialFilter={initialFilterHH}
              appliedFilter={appliedFilterHH}
              setAppliedFilter={setAppliedFilterHH}
              isOnPaper={false}
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
};
