import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Tab,
  Tabs,
} from '@material-ui/core';
import { Field, Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  useHouseholdChoiceDataQuery,
  useIndividualChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { FormikCheckboxField } from '../../../../shared/Formik/FormikCheckboxField';
import { GRIEVANCE_ISSUE_TYPES } from '../../../../utils/constants';
import { getFilterFromQueryParams } from '../../../../utils/utils';
import { AutoSubmitFormOnEnter } from '../../../core/AutoSubmitFormOnEnter';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { TabPanel } from '../../../core/TabPanel';
import { HouseholdFilters } from '../../../population/HouseholdFilter';
import { IndividualsFilter } from '../../../population/IndividualsFilter';
import { LookUpHouseholdTable } from '../LookUpHouseholdTable/LookUpHouseholdTable';
import { LookUpIndividualTable } from '../LookUpIndividualTable/LookUpIndividualTable';

const StyledTabs = styled(Tabs)`
  && {
    max-width: 500px;
  }
`;

export const LookUpHouseholdIndividualModal = ({
  onValueChange,
  initialValues,
  lookUpDialogOpen,
  setLookUpDialogOpen,
  selectedIndividual,
  selectedHousehold,
  setSelectedIndividual,
  setSelectedHousehold,
}: {
  onValueChange;
  initialValues;
  lookUpDialogOpen;
  setLookUpDialogOpen;
  selectedIndividual;
  selectedHousehold;
  setSelectedIndividual;
  setSelectedHousehold;
}): React.ReactElement => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const [selectedTab, setSelectedTab] = useState(0);
  const initialFilterHH = {
    search: '',
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
    lastRegistrationDate: '',
    status: '',
    orderBy: 'unicef_id',
  };

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

  if (householdChoicesLoading || individualChoicesLoading)
    return <LoadingComponent />;

  if (!individualChoicesData || !householdChoicesData) {
    return null;
  }

  const handleCancel = (): void => {
    setLookUpDialogOpen(false);
    setSelectedTab(0);
  };

  const shouldBeDisabled = (values): boolean => {
    const individualRequiredIssueTypes = [
      GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL,
      GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL,
    ];
    const householdRequiredIssueTypes = [
      GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD,
      GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD,
    ];
    const isHouseholdRequired = householdRequiredIssueTypes.includes(
      values.issueType,
    );
    const isIndividualRequired = individualRequiredIssueTypes.includes(
      values.issueType,
    );
    let result = false;
    if (isIndividualRequired) {
      result = !selectedIndividual || !values.identityVerified;
    } else if (isHouseholdRequired) {
      result = !selectedHousehold || !values.identityVerified;
    } else {
      result = !values.identityVerified;
    }
    return result;
  };

  return (
    <Formik
      initialValues={initialValues}
      enableReinitialize
      onSubmit={(values) => {
        onValueChange('selectedHousehold', values.selectedHousehold);
        onValueChange('selectedIndividual', values.selectedIndividual);
        setLookUpDialogOpen(false);
      }}
    >
      {({ submitForm, setFieldValue, values }) => (
        <Dialog
          maxWidth='lg'
          fullWidth
          open={lookUpDialogOpen}
          onClose={() => setLookUpDialogOpen(false)}
          scroll='paper'
          aria-labelledby='form-dialog-title'
        >
          {lookUpDialogOpen && <AutoSubmitFormOnEnter />}
          <DialogTitleWrapper>
            <DialogTitle>
              <StyledTabs
                value={selectedTab}
                onChange={(event: React.ChangeEvent<{}>, newValue: number) => {
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
            </DialogTitle>
          </DialogTitleWrapper>
          <DialogContent>
            <TabPanel value={selectedTab} index={0}>
              <HouseholdFilters
                filter={filterHH}
                choicesData={householdChoicesData}
                setFilter={setFilterHH}
                initialFilter={initialFilterHH}
                appliedFilter={appliedFilterHH}
                setAppliedFilter={setAppliedFilterHH}
              />
              <LookUpHouseholdTable
                filter={appliedFilterHH}
                businessArea={businessArea}
                choicesData={householdChoicesData}
                setFieldValue={setFieldValue}
                selectedHousehold={selectedHousehold}
                setSelectedHousehold={setSelectedHousehold}
                setSelectedIndividual={setSelectedIndividual}
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
              />
              <LookUpIndividualTable
                filter={appliedFilterIND}
                businessArea={businessArea}
                setFieldValue={setFieldValue}
                valuesInner={values}
                selectedHousehold={selectedHousehold}
                setSelectedHousehold={setSelectedHousehold}
                selectedIndividual={selectedIndividual}
                setSelectedIndividual={setSelectedIndividual}
              />
            </TabPanel>
          </DialogContent>
          <DialogFooter>
            <DialogActions>
              <Box display='flex'>
                <Box mr={1}>
                  <Field
                    name='identityVerified'
                    label={t('Identity Verified*')}
                    component={FormikCheckboxField}
                  />
                </Box>
                <Button onClick={() => handleCancel()}>{t('CANCEL')}</Button>
                <Button
                  color='primary'
                  variant='contained'
                  onClick={async () => {
                    await submitForm();
                  }}
                  disabled={shouldBeDisabled(values)}
                  data-cy='button-submit'
                >
                  {t('SAVE')}
                </Button>
              </Box>
            </DialogActions>
          </DialogFooter>
        </Dialog>
      )}
    </Formik>
  );
};
