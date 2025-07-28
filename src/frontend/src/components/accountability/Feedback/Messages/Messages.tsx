import withErrorBoundary from '@components/core/withErrorBoundary';
import { LoadingButton } from '@core/LoadingButton';
import { OverviewContainerColumn } from '@core/OverviewContainerColumn';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Avatar, Box, Grid2 as Grid, Paper, Typography } from '@mui/material';
import { FeedbackDetail } from '@restgenerated/models/FeedbackDetail';
import { RestService } from '@restgenerated/services/RestService';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { renderUserName, showApiErrorMessages } from '@utils/utils';
import { Field, Form, Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';

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

interface MessagesProps {
  messages: FeedbackDetail['feedbackMessages'];
  canAddMessage: boolean;
}

function Messages({ messages, canAddMessage }: MessagesProps): ReactElement {
  const { t } = useTranslation();
  const { businessAreaSlug, programSlug } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const { data: meData, isLoading: meLoading } = useQuery({
    queryKey: ['profile', businessAreaSlug, programSlug],
    queryFn: () => {
      return RestService.restBusinessAreasUsersProfileRetrieve({
        businessAreaSlug,
        program: programSlug,
      });
    },
    staleTime: 5 * 60 * 1000, // Data is considered fresh for 5 minutes
    gcTime: 30 * 60 * 1000, // Keep unused data in cache for 30 minutes
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
  });

  const { id } = useParams();
  const [loading, setLoading] = useState<boolean>(false);
  const queryClient = useQueryClient();

  const createFeedbackMessage = async (description: string) => {
    if (!id || !businessAreaSlug) return;

    try {
      setLoading(true);
      await RestService.restBusinessAreasFeedbacksMessageCreate({
        businessAreaSlug,
        id,
        requestBody: { description },
      });

      queryClient.invalidateQueries({
        queryKey: ['businessAreasFeedbacksRetrieve', id],
      });
    } catch (error) {
      showApiErrorMessages(error, showMessage);
    } finally {
      setLoading(false);
    }
  };

  if (meLoading) {
    return null;
  }

  const note = (
    name: string,
    date: string,
    description: string,
    noteId: string,
  ): ReactElement => (
    <Grid container key={noteId}>
      <Grid size={{ xs: 2 }}>
        <Avatar alt={`${name} picture`} src="/static/images/avatar/1.jpg" />
      </Grid>
      <Grid size={{ xs: 10 }}>
        <Grid size={{ xs: 12 }}>
          <Box display="flex" justifyContent="space-between">
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

  const mappedMessages = messages?.map((el) =>
    note(el.createdBy, el.createdAt, el.description, el.id),
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
          onSubmit={async (values, { resetForm }) => {
            await createFeedbackMessage(values.newNote);
            resetForm({});
          }}
          validationSchema={validationSchema}
        >
          {({ submitForm }) => (
            <StyledBox>
              <Title>
                <Typography variant="h6">{t('Notes')}</Typography>
              </Title>
              <OverviewContainerColumn>
                {mappedMessages}
                {canAddMessage && (
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
                              label="Add a message ..."
                              component={FormikTextField}
                            />
                            <Box
                              mt={2}
                              display="flex"
                              justifyContent="flex-end"
                            >
                              <LoadingButton
                                loading={loading}
                                color="primary"
                                variant="contained"
                                onClick={submitForm}
                              >
                                {t('Send New Message')}
                              </LoadingButton>
                            </Box>
                          </Form>
                        </DescMargin>
                      </Grid>
                    </Grid>
                  </Grid>
                )}
              </OverviewContainerColumn>
            </StyledBox>
          )}
        </Formik>
      </Box>
    </Grid>
  );
}

export default withErrorBoundary(Messages, 'Messages');
