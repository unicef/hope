import { Box, Button } from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import { FieldArray } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { AllAreasTreeQuery } from '../../../__generated__/graphql';
import { BaseSection } from '../../core/BaseSection';
import { ButtonTooltip } from '../../core/ButtonTooltip';
import { ProgramPartnerCard } from './ProgramPartnerCard';

interface PartnersStepProps {
  values;
  allAreasTreeData: AllAreasTreeQuery['allAreasTree'];
  partnerChoices;
  step: number;
  setStep: (step: number) => void;
}

export const PartnersStep: React.FC<PartnersStepProps> = ({
  values,
  allAreasTreeData,
  partnerChoices,
  step,
  setStep,
}) => {
  const { t } = useTranslation();
  const title = t('Programme Partners');
  const description = t(
    'Provide info about Programme Partner and set Area Access',
  );

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
    <BaseSection title={title} description={description}>
      <FieldArray
        name='partners'
        render={(arrayHelpers) => {
          const {
            form: { setFieldValue },
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
                  setFieldValue={setFieldValue}
                />
              ))}
              <Box display='flex' justifyContent='space-between'>
                <ButtonTooltip
                  disabled={addPartnerDisabled}
                  data-cy='button-add-partner'
                  title={tooltipText}
                  onClick={() =>
                    arrayHelpers.push({ id: '', areaAccess: 'BUSINESS_AREA' })
                  }
                  variant='outlined'
                  color='primary'
                  endIcon={<AddIcon />}
                >
                  {t('Add Partner')}
                </ButtonTooltip>
                <Button
                  data-cy='button-back'
                  variant='outlined'
                  onClick={() => setStep(step - 1)}
                  disabled={step === 0}
                >
                  {t('Back')}
                </Button>
              </Box>
            </>
          );
        }}
      />
    </BaseSection>
  );
};
