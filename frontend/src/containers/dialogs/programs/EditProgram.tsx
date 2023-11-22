import { Button } from '@material-ui/core';
import EditIcon from '@material-ui/icons/EditRounded';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ProgramQuery,
  useUpdateProgramMutation,
} from '../../../__generated__/graphql';
import { ALL_LOG_ENTRIES_QUERY } from '../../../apollo/queries/core/AllLogEntries';
import { PROGRAM_QUERY } from '../../../apollo/queries/program/Program';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { decodeIdString } from '../../../utils/utils';
import { ProgramForm } from '../../forms/ProgramForm';
import {useProgramContext} from "../../../programContext";

interface EditProgramProps {
  program: ProgramQuery['program'];
}

export const EditProgram = ({ program }: EditProgramProps): ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const { setSelectedProgram } = useProgramContext();

  const [mutate, { loading }] = useUpdateProgramMutation({
    refetchQueries: [
      {
        query: ALL_LOG_ENTRIES_QUERY,
        variables: {
          objectId: decodeIdString(program.id),
          count: 5,
          businessArea,
        },
      },
    ],
    update(cache, { data: { updateProgram } }) {
      cache.writeQuery({
        query: PROGRAM_QUERY,
        variables: {
          id: program.id,
        },
        data: { program: updateProgram.program },
      });
    },
  });
  const submitFormHandler = async (values): Promise<void> => {
    try {
      const response = await mutate({
        variables: {
          programData: {
            id: program.id,
            ...values,
            startDate: values.startDate,
            endDate: values.endDate,
            budget: parseFloat(values.budget).toFixed(2),
          },
          version: program.version,
        },
      });

      const { id, name, status, individualDataNeeded, dataCollectingType } = response.data.updateProgram.program
      setSelectedProgram({
        id,
        name,
        status,
        individualDataNeeded,
        dataCollectingType: {
          id: dataCollectingType?.id,
          householdFiltersAvailable: dataCollectingType?.householdFiltersAvailable,
          individualFiltersAvailable: dataCollectingType?.individualFiltersAvailable,
        }
      })

      showMessage(t('Programme edited.'), {
        pathname: `/${baseUrl}/details/${response.data.updateProgram.program.id}`,
      });
      setOpen(false);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const renderSubmit = (submit): ReactElement => {
    return (
      <>
        <Button onClick={() => setOpen(false)}>Cancel</Button>
        <LoadingButton
          loading={loading}
          onClick={submit}
          type='submit'
          color='primary'
          variant='contained'
          data-cy='button-save'
        >
          {t('Save')}
        </LoadingButton>
      </>
    );
  };

  return (
    <span>
      <Button
        data-cy='button-edit-program'
        variant='outlined'
        color='primary'
        startIcon={<EditIcon />}
        onClick={() => setOpen(true)}
      >
        {t('EDIT PROGRAMME')}
      </Button>
      <ProgramForm
        onSubmit={submitFormHandler}
        renderSubmit={renderSubmit}
        program={program}
        open={open}
        onClose={() => setOpen(false)}
        title={t('Edit Programme Details')}
      />
    </span>
  );
};
