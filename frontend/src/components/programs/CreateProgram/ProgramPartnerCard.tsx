import React from 'react';
import { useTranslation } from 'react-i18next';
import { BaseSection } from '../../core/BaseSection';
import { Box, Button } from '@material-ui/core';
import { Formik, Form } from 'formik';
import { DeleteProgramPartner } from './DeleteProgramPartner';

interface ProgramPartnerAccessCardProps {
  partner;
  handleDeleteProgramPartner: (id: string) => void;
}

export const ProgramPartnerAccessCard: React.FC<ProgramPartnerAccessCardProps> = ({
  partner,
  handleDeleteProgramPartner,
}): React.ReactElement => {
  const { t } = useTranslation();

  const initialValues = {
    // Define your initial values here
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        // eslint-disable-next-line no-console
        console.log(values);
      }}
    >
      {({ submitForm }) => {
        const buttons = (
          <>
            <Box display='flex' justifyContent='center' alignItems='center'>
              <Box mr={4}>
                <DeleteProgramPartner
                  partner={partner}
                  //TODO: add permission
                  canDeleteProgramPartner
                  handleDeleteProgramPartner={handleDeleteProgramPartner}
                />
              </Box>
              <Button onClick={submitForm} variant='contained' color='primary'>
                {t('Save')}
              </Button>
            </Box>
          </>
        );

        return (
          <Form>
            <BaseSection title={t('Programme Partner')} buttons={buttons}>
              <div>Partner: {partner.id}</div>
            </BaseSection>
          </Form>
        );
      }}
    </Formik>
  );
};
