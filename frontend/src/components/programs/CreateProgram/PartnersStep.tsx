import { Button } from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import { FieldArray } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { v4 as uuidv4 } from 'uuid';
import { BaseSection } from '../../core/BaseSection';
import { ProgramPartnerCard } from './ProgramPartnerCard';

interface PartnersStepProps {
  values;
  allAreasTree;
}

export const PartnersStep: React.FC<PartnersStepProps> = ({
  values,
  allAreasTree,
}) => {
  const { t } = useTranslation();
  const title = t('Programme Partners');
  const description = t(
    'Provide info about Programme Partner and set Area Access',
  );

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
                  allAreasTree={allAreasTree}
                  setFieldValue={setFieldValue}
                />
              ))}
              <Button
                onClick={() => arrayHelpers.push({ id: uuidv4() })}
                variant='outlined'
                color='primary'
                endIcon={<AddIcon />}
              >
                {t('Add Partner')}
              </Button>
            </>
          );
        }}
      />
    </BaseSection>
  );
};
