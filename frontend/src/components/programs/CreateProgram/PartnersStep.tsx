import { Box, Button, Grid } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { Field, FieldArray, FormikErrors } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { AllAreasTreeQuery, ProgramPartnerAccess } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { BaseSection } from '@core/BaseSection';
import { ButtonTooltip } from '@core/ButtonTooltip';
import { ProgramPartnerCard } from './ProgramPartnerCard';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { DividerLine } from '@core/DividerLine';
import { useEffect } from 'react';

interface PartnersStepProps {
  values;
  allAreasTreeData: AllAreasTreeQuery['allAreasTree'];
  partnerChoices;
  step: number;
  setStep: (step: number) => void;
  submitForm: () => void;
  setFieldValue;
}

export const PartnersStep: React.FC<PartnersStepProps> = ({
  values,
  allAreasTreeData,
  partnerChoices,
  step,
  setStep,
  submitForm,
  setFieldValue,
}) => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  useEffect(() => {
    if (values.partners.length === 0) {
      setFieldValue('partners', [
        {
          id: '',
          areaAccess: 'BUSINESS_AREA',
        },
      ]);
    }
  }, [values, setFieldValue]);

  const title = t('Programme Partners');

  const addPartnerDisabled =
    partnerChoices.every((choice) => choice.disabled) ||
    values.partners.some((partner) => !partner.id);

  let tooltipText = '';
  if (addPartnerDisabled) {
    if (values.partners.some((partner) => !partner.id)) {
      tooltipText = t('Select partner first');
    } else {
      tooltipText = t('All partners have been added');
    }
  }

  const accessTypeChoices = [
    {
      value: ProgramPartnerAccess.NonePartnersAccess,
      label: 'None of the partners should have access',
    },
    {
      value: ProgramPartnerAccess.SelectedPartnersAccess,
      label: 'Only selected partners within the business area',
    },
    {
      value: ProgramPartnerAccess.AllPartnersAccess,
      label: 'All partners within the business area',
    },
  ];

  return (
    <BaseSection title={title}>
      <>
        <Box display="flex" justifyContent="space-between" mt={2}>
          <Grid item xs={6}>
            <Field
              name="partnerAccess"
              label={t('Who should have access to the program?')}
              color="primary"
              choices={accessTypeChoices}
              component={FormikSelectField}
              required
              disableClearable
            />
          </Grid>
        </Box>
        {values.partnerAccess === ProgramPartnerAccess.SelectedPartnersAccess && (
          <>
            <DividerLine />
            <FieldArray
              name="partners"
              render={(arrayHelpers) => {
                const {
                  form: { setFieldValue: setArrayFieldValue },
                } = arrayHelpers;
                return (
                  <>
                    {values.partners.map((partner, index) => (
                      <ProgramPartnerCard
                        key={partner.id}
                        partner={partner}
                        index={index}
                        values={values}
                        arrayHelpers={arrayHelpers}
                        allAreasTreeData={allAreasTreeData}
                        partnerChoices={partnerChoices}
                        setFieldValue={setArrayFieldValue}
                        canDeleteProgramPartner={values.partners.length > 1}
                      />
                    ))}
                    <Box display="flex">
                      <ButtonTooltip
                        disabled={addPartnerDisabled}
                        data-cy="button-add-partner"
                        title={tooltipText}
                        onClick={() =>
                          arrayHelpers.push({
                            id: '',
                            areaAccess: 'BUSINESS_AREA',
                          })
                        }
                        variant="outlined"
                        color="primary"
                        endIcon={<AddIcon />}
                      >
                        {t('Add Partner')}
                      </ButtonTooltip>
                    </Box>
                  </>
                );
              }}
            />
          </>
        )}
        <Box display="flex" justifyContent="flex-end">
          <Box display="flex">
            <Box mr={2}>
              <Button
                data-cy="button-cancel"
                component={Link}
                to={`/${baseUrl}/list`}
              >
                {t('Cancel')}
              </Button>
            </Box>
            <Box mr={2}>
              <Button
                data-cy="button-back"
                variant="outlined"
                onClick={() => setStep(step - 1)}
              >
                {t('Back')}
              </Button>
            </Box>
            <Button
              data-cy="button-save"
              variant="contained"
              color="primary"
              onClick={submitForm}
            >
              {t('Save')}
            </Button>
          </Box>
        </Box>
      </>
    </BaseSection>
  );
};
