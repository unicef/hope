import { Box, Button, Grid } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { Field, FieldArray } from 'formik';
import * as React from 'react';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { AllAreasTreeQuery, ProgramPartnerAccess } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ButtonTooltip } from '@core/ButtonTooltip';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { DividerLine } from '@core/DividerLine';
import { partnerAccessChoices } from '@components/programs/constants';
import { ProgramPartnerCard } from '../CreateProgram/ProgramPartnerCard';

interface PartnersStepProps {
  values;
  allAreasTreeData: AllAreasTreeQuery['allAreasTree'];
  partnerChoices;
  submitForm: () => void;
  setFieldValue;
  programId?: string;
}

export const PartnersStep: React.FC<PartnersStepProps> = ({
  values,
  allAreasTreeData,
  partnerChoices,
  submitForm,
  setFieldValue,
  programId: formProgramId,
}) => {
  const { t } = useTranslation();
  const { baseUrl, programId, businessArea } = useBaseUrl();

  useEffect(() => {
    if (
      values.partnerAccess === ProgramPartnerAccess.SelectedPartnersAccess &&
      values.partners.length === 0
    ) {
      setFieldValue('partners', [
        {
          id: '',
          areaAccess: 'BUSINESS_AREA',
        },
      ]);
    }

    if (
      values.partnerAccess !== ProgramPartnerAccess.SelectedPartnersAccess &&
      values.partners.length > 0
    ) {
      setFieldValue('partners', []);
    }
  }, [values, setFieldValue]);

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

  return (
    <>
      <Box display="flex" justifyContent="space-between" mt={2}>
        <Grid item xs={6}>
          <Field
            name="partnerAccess"
            label={t('Who should have access to the program?')}
            color="primary"
            choices={partnerAccessChoices}
            component={FormikSelectField}
            required
            disableClearable
          />
        </Grid>
      </Box>
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
                  {values.partnerAccess ===
                    ProgramPartnerAccess.SelectedPartnersAccess && (
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
                  )}
                </Box>
                {values.partnerAccess ===
                  ProgramPartnerAccess.AllPartnersAccess && (
                  <Grid container>
                    <Grid item xs={6}>
                      <Field
                        name={`partners[${0}].id`}
                        label={t('Partner')}
                        color="primary"
                        choices={partnerChoices}
                        component={FormikSelectField}
                        required
                      />
                    </Grid>
                  </Grid>
                )}
              </>
            );
          }}
        />
      </>
      <Box mt={1} display="flex" justifyContent="space-between">
        <Box mr={2}>
          <Button
            data-cy="button-cancel"
            component={Link}
            to={
              formProgramId
                ? `/${businessArea}/programs/${programId}/details/${formProgramId}`
                : `/${baseUrl}/list`
            }
          >
            {t('Cancel')}
          </Button>
        </Box>
        <Box display="flex">
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
  );
};
