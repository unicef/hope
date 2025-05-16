import { Avatar, Box, Grid2 as Grid, Paper, Typography } from '@mui/material';
import { Field, Form, Formik } from 'formik';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { renderUserName } from '@utils/utils';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useCreateGrievanceTicketNoteMutation,
} from '@generated/graphql';
import { LoadingButton } from '@core/LoadingButton';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { useProgramContext } from '../../../programContext';
import { ReactElement } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';

const Name = styled.span`
  font-size: 16px;
`;
const Date = styled.span`
  font-size: 12px;
  color: #848484;
`;
const DescMargin = styled.div`
  margin-bottom: 35px;
`;
const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

export function Notes({
  notes,
  canAddNote,
}: {
  notes: GrievanceTicketQuery['grievanceTicket']['ticketNotes'];
  canAddNote: boolean;
}): ReactElement {
  const { t } = useTranslation();
  const { businessAreaSlug, programSlug } = useBaseUrl();

  const { data: meData, isLoading: meLoading } = useQuery({
    queryKey: ['profile', businessAreaSlug, programSlug],
    queryFn: () => {
      return RestService.restBusinessAreasUsersProfileRetrieve({
        businessAreaSlug,
        program: programSlug === 'all' ? undefined : programSlug,
      });
    },
    staleTime: 5 * 60 * 1000, // Data is considered fresh for 5 minutes
    gcTime: 30 * 60 * 1000, // Keep unused data in cache for 30 minutes
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
  });

  const { id } = useParams();
  const { isActiveProgram } = useProgramContext();
  const [mutate, { loading }] = useCreateGrievanceTicketNoteMutation();

  if (meLoading) {
    return null;
  }

  const note = (
    name: string,
    date: string,
    description: string,
    noteId: string,
  ): ReactElement => (
    <Grid container key={noteId} data-cy="note-row">
      <Grid size={{ xs: 2 }}>
        <Avatar alt={`${name} picture`} src="/static/images/avatar/1.jpg" />
      </Grid>
      <Grid size={{ xs: 10 }}>
        <Grid size={{ xs: 12 }}>
          <Box
            display="flex"
            justifyContent="space-between"
            data-cy="note-name"
          >
            <Name>{name}</Name>
            <Date>
              <UniversalMoment withTime>{date}</UniversalMoment>
            </Date>
          </Box>
        </Grid>
        <Grid size={{ xs: 12 }}>
          <DescMargin>
            <p>{description}</p>
          </DescMargin>
        </Grid>
      </Grid>
    </Grid>
  );

  const mappedNotes = notes?.edges?.map((el) =>
    note(
      renderUserName(el.node.createdBy),
      el.node.createdAt,
      el.node.description,
      el.node.id,
    ),
  );

  const initialValues: { [key: string]: string } = {
    newNote: '',
  };

  const validationSchema = Yup.object().shape({
    newNote: Yup.string().required(t('Note cannot be empty')),
  });

  const myName = `${meData.firstName || meData.email}`;

  return (
    <Grid size={{ xs: 8 }}>
      <Box p={3}>
        <Formik
          initialValues={initialValues}
          onSubmit={(values, { resetForm }) => {
            mutate({
              variables: {
                noteInput: { ticket: id, description: values.newNote },
              },
              refetchQueries: () => [
                { query: GrievanceTicketDocument, variables: { id } },
              ],
            });
            resetForm({});
          }}
          validationSchema={validationSchema}
        >
          {({ submitForm }) => (
            <StyledBox>
              <Title>
                <Typography variant="h6">Notes</Typography>
              </Title>
              {mappedNotes}
              {canAddNote && (
                <Grid container>
                  <Grid size={{ xs: 2 }}>
                    <Avatar src={myName} alt={myName} />
                  </Grid>
                  <Grid size={{ xs: 10 }}>
                    <Grid size={{ xs: 12 }}>
                      <Box display="flex" justifyContent="space-between">
                        <Name>{renderUserName(meData)}</Name>
                      </Box>
                    </Grid>
                    <Grid size={{ xs: 12 }}>
                      <DescMargin>
                        <Form>
                          <Field
                            name="newNote"
                            multiline
                            fullWidth
                            variant="filled"
                            label="Add a note ..."
                            component={FormikTextField}
                          />
                          <Box mt={2} display="flex" justifyContent="flex-end">
                            <LoadingButton
                              data-cy="button-add-note"
                              loading={loading}
                              color="primary"
                              variant="contained"
                              onClick={submitForm}
                              disabled={!isActiveProgram}
                            >
                              {t('Add New Note')}
                            </LoadingButton>
                          </Box>
                        </Form>
                      </DescMargin>
                    </Grid>
                  </Grid>
                </Grid>
              )}
            </StyledBox>
          )}
        </Formik>
      </Box>
    </Grid>
  );
}
