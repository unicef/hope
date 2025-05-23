import { LoadingComponent } from '@core/LoadingComponent';
import { TabPanel } from '@core/TabPanel';
import { Tab, Tabs } from '@core/Tabs';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box } from '@mui/material';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { GRIEVANCE_ISSUE_TYPES } from '@utils/constants';
import { getFilterFromQueryParams } from '@utils/utils';
import get from 'lodash/get';
import { ChangeEvent, ReactElement, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { HouseholdFilters } from '../../../population/HouseholdFilter';
import { IndividualsFilter } from '../../../population/IndividualsFilter';
import { LookUpHouseholdTable } from '../LookUpHouseholdTable/LookUpHouseholdTable';
import { LookUpIndividualTable } from '../LookUpIndividualTable/LookUpIndividualTable';
import { PaginatedProgramListList } from '@restgenerated/models/PaginatedProgramListList';
import { createApiParams } from '@utils/apiUtils';

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
  selectedHousehold: HouseholdDetail;
  setSelectedIndividual;
  setSelectedHousehold;
  redirectedFromRelatedTicket?: boolean;
  isFeedbackWithHouseholdOnly?: boolean;
}): ReactElement {
  const location = useLocation();
  const { businessArea, isAllPrograms, programId } = useBaseUrl();
  const { isSocialDctType } = useProgramContext();
  const [selectedTab, setSelectedTab] = useState(isSocialDctType ? 1 : 0);

  const { data: householdChoicesData, isLoading: householdChoicesLoading } =
    useQuery<HouseholdChoices>({
      queryKey: ['householdChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasHouseholdsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const { data: individualChoicesData, isLoading: individualChoicesLoading } =
    useQuery<IndividualChoices>({
      queryKey: ['individualChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasIndividualsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const initialFilterHH = {
    program: isAllPrograms ? '' : programId,
    search: '',
    documentType: householdChoicesData?.documentTypeChoices?.[0]?.value,
    documentNumber: '',
    residenceStatus: '',
    admin1: '',
    admin2: '',
    householdSizeMin: '',
    householdSizeMax: '',
    orderBy: 'unicef_id',
    withdrawn: '',
    programState: 'active',
  };
  const initialFilterIND = {
    program: isAllPrograms ? '' : programId,
    search: '',
    documentType: individualChoicesData?.documentTypeChoices?.[0]?.value,
    documentNumber: '',
    admin2: '',
    sex: '',
    ageMin: '',
    ageMax: '',
    flags: [],
    orderBy: 'unicef_id',
    status: '',
    programState: 'active',
  };

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

  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const { data: programsData, isLoading: programsLoading } =
    useQuery<PaginatedProgramListList>({
      queryKey: ['businessAreasProgramsList', { first: 100 }, businessArea],
      queryFn: () =>
        RestService.restBusinessAreasProgramsList(
          createApiParams(
            { businessAreaSlug: businessArea, first: 100 },
            {
              withPagination: false,
            },
          ),
        ),
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
            value={isSocialDctType ? 0 : selectedTab}
            onChange={(_event: ChangeEvent<object>, newValue: number) => {
              setSelectedTab(newValue);
            }}
            indicatorColor="primary"
            textColor="primary"
            variant="fullWidth"
            aria-label="look up tabs"
          >
            {!isSocialDctType && (
              <Tab
                data-cy="look-up-household"
                label={`LOOK UP ${beneficiaryGroup?.groupLabel}`}
              />
            )}
            <Tab
              disabled={
                initialValues.issueType ===
                  GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL ||
                initialValues.issueType ===
                  GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD ||
                initialValues.issueType === GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD
              }
              data-cy="look-up-individual"
              label={`LOOK UP ${beneficiaryGroup?.memberLabel}`}
            />
          </StyledTabs>
        </Box>
      </Box>
      <Box>
        {!isSocialDctType && (
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
        )}

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
