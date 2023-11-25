import { Button, Dialog, IconButton } from '@material-ui/core';
import { FileCopy } from '@material-ui/icons';
import React, { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { useTranslation } from 'react-i18next';
import {
  AllProgramsForChoicesDocument,
  ProgramQuery,
  useCopyProgramMutation,
} from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { Formik } from 'formik';
import { programValidationSchema } from '../../../components/programs/CreateProgram/programValidationSchema';
import { ProgramForm } from '../../forms/ProgramForm';
import { DialogContainer } from '../DialogContainer';

interface CopyProgramProps {
  program: ProgramQuery['program'];
}

export const CopyProgram = ({
  program,
}: CopyProgramProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const [mutate] = useCopyProgramMutation();

  const {
    name,
    startDate,
    endDate,
    sector,
    dataCollectingType,
    description,
    budget = '0.00',
    administrativeAreasOfImplementation,
    populationGoal = 0,
    cashPlus = false,
    frequencyOfPayments = 'REGULAR',
  } = program;

  const handleSubmit = async (values): Promise<void> => {
    try {
      const response = await mutate({
        variables: {
          programData: {
            ...values,
            businessAreaSlug: businessArea,
          },
        },
        refetchQueries: () => [
          {
            query: AllProgramsForChoicesDocument,
            variables: { businessArea, first: 100 },
          },
        ],
      });
      showMessage('Programme created.', {
        pathname: `/${baseUrl}/details/${response.data.copyProgram.program.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  //TODO: remove this
  const partners = [{ id: uuidv4() }, { id: uuidv4() }, { id: uuidv4() }];

  const initialValues = {
    name,
    startDate,
    endDate,
    sector,
    dataCollectingTypeCode: dataCollectingType?.code,
    description,
    budget,
    administrativeAreasOfImplementation,
    populationGoal,
    cashPlus,
    frequencyOfPayments,
    partners,
  };

  return (
    <>
      {/* //TODO: fix this view */}
      {/* <IconButton data-cy='button-copy-program' onClick={() => setOpen(true)}>
        <FileCopy />
      </IconButton> */}
      <DialogContainer>
        <Dialog open={open} onClose={() => setOpen(false)} scroll='paper'>
          <Formik
            initialValues={initialValues}
            onSubmit={(values) => {
              handleSubmit(values);
            }}
            validationSchema={programValidationSchema(t)}
          >
            {({ values }) => <ProgramForm values={values} />}
          </Formik>
        </Dialog>
      </DialogContainer>
    </>
  );
};
