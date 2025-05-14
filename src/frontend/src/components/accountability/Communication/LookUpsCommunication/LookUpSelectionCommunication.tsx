import { Box, FormControlLabel, Radio, RadioGroup } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { RegistrationDataImportStatus } from '@generated/graphql';
import { CommunicationTabsValues } from '@utils/constants';
import { getFilterFromQueryParams } from '@utils/utils';
import { LookUpHouseholdFiltersCommunication } from './LookUpHouseholdFiltersCommunication';
import { LookUpRegistrationFiltersCommunication } from './LookUpRegistrationFiltersCommunication';
import { LookUpSelectionTablesCommunication } from './LookUpSelectionTablesCommunication';
import { LookUpTargetPopulationFiltersCommunication } from './LookUpTargetPopulationFiltersCommunication';
import { useProgramContext } from 'src/programContext';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

const BoxWithBorderBottom = styled(Box)`
  border-bottom: 1px solid #e4e4e4;
  padding: 15px 0;
`;

export function LookUpSelectionCommunication({
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
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const communicationTabs = [
    `${beneficiaryGroup?.groupLabel}`,
    'Target Population',
    'RDI',
  ];

  const initialFilterRDI = {
    search: '',
    importedBy: '',
    status: RegistrationDataImportStatus.Merged,
    totalHouseholdsCountWithValidPhoneNoMin: '',
    totalHouseholdsCountWithValidPhoneNoMax: '',
    importDateRangeMin: '',
    importDateRangeMax: '',
  };

  const [filterRDI, setFilterRDI] = useState(
    getFilterFromQueryParams(location, initialFilterRDI),
  );
  const [appliedFilterRDI, setAppliedFilterRDI] = useState(
    getFilterFromQueryParams(location, initialFilterRDI),
  );

  const initialFilterTP = {
    name: '',
    status: '',
    totalHouseholdsCountWithValidPhoneNoMin: '',
    totalHouseholdsCountWithValidPhoneNoMax: '',
    createdAtRangeMin: '',
    createdAtRangeMax: '',
  };

  const [filterTP, setFilterTP] = useState(
    getFilterFromQueryParams(location, initialFilterTP),
  );
  const [appliedFilterTP, setAppliedFilterTP] = useState(
    getFilterFromQueryParams(location, initialFilterTP),
  );

  const { data: choicesData, isLoading: choicesLoading } =
    useQuery<HouseholdChoices>({
      queryKey: ['householdChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasHouseholdsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const initialFilterHH = {
    search: '',
    documentType: choicesData?.documentTypeChoices?.[0]?.value,
    documentNumber: '',
    residenceStatus: '',
    admin2: '',
    householdSizeMin: '',
    householdSizeMax: '',
    orderBy: 'unicef_id',
    withdrawn: '',
  };

  const [filterHH, setFilterHH] = useState(
    getFilterFromQueryParams(location, initialFilterHH),
  );
  const [appliedFilterHH, setAppliedFilterHH] = useState(
    getFilterFromQueryParams(location, initialFilterHH),
  );

  const { t } = useTranslation();

  const handleChange = (type: number, value: string[] | string): void => {
    setValues({
      ...values,
      households:
        type === CommunicationTabsValues.HOUSEHOLD && typeof value !== 'string'
          ? value
          : [],
      targetPopulation:
        type === CommunicationTabsValues.TARGET_POPULATION &&
        typeof value === 'string'
          ? value
          : '',
      registrationDataImport:
        type === CommunicationTabsValues.RDI && typeof value === 'string'
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
          {communicationTabs.map((tab, index) => (
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
        {selectedTab === CommunicationTabsValues.HOUSEHOLD && (
          <LookUpHouseholdFiltersCommunication
            filter={filterHH}
            choicesData={choicesData}
            setFilter={setFilterHH}
            initialFilter={initialFilterHH}
            appliedFilter={appliedFilterHH}
            setAppliedFilter={setAppliedFilterHH}
          />
        )}
        {selectedTab === CommunicationTabsValues.TARGET_POPULATION && (
          <LookUpTargetPopulationFiltersCommunication
            filter={filterTP}
            setFilter={setFilterTP}
            initialFilter={initialFilterTP}
            appliedFilter={appliedFilterTP}
            setAppliedFilter={setAppliedFilterTP}
          />
        )}
        {selectedTab === CommunicationTabsValues.RDI && (
          <LookUpRegistrationFiltersCommunication
            filter={filterRDI}
            setFilter={setFilterRDI}
            initialFilter={initialFilterRDI}
            appliedFilter={appliedFilterRDI}
            setAppliedFilter={setAppliedFilterRDI}
          />
        )}
      </Box>
      <LookUpSelectionTablesCommunication
        selectedTab={selectedTab}
        choicesData={choicesData}
        filtersHouseholdApplied={appliedFilterHH}
        filtersTargetPopulationApplied={appliedFilterTP}
        filtersRDIApplied={appliedFilterRDI}
        onValueChange={onValueChange}
        values={values}
        handleChange={handleChange}
        businessArea={businessArea}
      />
    </Box>
  );
}
