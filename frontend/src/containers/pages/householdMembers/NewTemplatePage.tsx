import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { PageHeader } from '@components/core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { BaseSection } from '@components/core/BaseSection';
import { Button, Stepper, Step, StepLabel } from '@mui/material';
import { getFilterFromQueryParams } from '@utils/utils';
import { FilterIndividuals } from '@components/periodicDataUpdates/FilterIndividuals';

export const NewTemplatePage = (): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  const location = useLocation();

  const initialFilter = {
    registrationDataImport: '',
    genderIdentity: '',
    ageMin: null,
    ageMax: null,
    hasGrievanceTicket: '',
    receivedAssistance: '',
    householdSizeMin: null,
    householdSizeMax: null,
  };

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Household Members'),
      to: `/${baseUrl}/population/household-members`,
    },
  ];

  const [activeStep, setActiveStep] = useState(0);
  const steps = ['Filter Individuals', 'Fields to Update'];

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  return (
    <>
      <PageHeader
        title={t('New Template Page')}
        breadCrumbs={
          hasPermissions(
            PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_LIST,
            permissions,
          )
            ? breadCrumbsItems
            : null
        }
      />
      <BaseSection
        title="New Template"
        buttons={
          <Button
            variant="contained"
            color="primary"
            component={Link}
            to="/new-template"
            startIcon={<AddIcon />}
          >
            New Template
          </Button>
        }
      >
        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        {activeStep === 0 && (
          <FilterIndividuals
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        )}
        {activeStep === 1 && <div>Fields to Update</div>}
        <div>
          <Button
            variant="outlined"
            color="secondary"
            component={Link}
            to="/household-members/periodic-data-updates"
            style={{ marginRight: '10px' }}
          >
            Cancel
          </Button>
          {activeStep === steps.length ? (
            <div>
              <Button onClick={handleBack}>Back</Button>
            </div>
          ) : (
            <div>
              <Button variant="contained" color="primary" onClick={handleNext}>
                {activeStep === steps.length - 1 ? 'Generate Template' : 'Next'}
              </Button>
            </div>
          )}
        </div>
      </BaseSection>
    </>
  );
};
